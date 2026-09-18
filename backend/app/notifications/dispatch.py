from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx
from sqlmodel import Session, select

from app.agent.events import EVENT_DEADLINE_REMINDER, EVENT_NEW_MATCHES, AgentEvent, bus
from app.config import get_settings
from app.db.models import NotificationChannel
from app.db.session import engine

logger = logging.getLogger(__name__)


class NotificationAdapter(ABC):
    channel: str

    @abstractmethod
    def send(self, subject: str, body: str, config: dict[str, Any]) -> None:
        raise NotImplementedError


class ConsoleNotifier(NotificationAdapter):
    channel = "console"

    def send(self, subject: str, body: str, config: dict[str, Any]) -> None:
        logger.info("[console notify] %s | %s", subject, body)


class EmailNotifier(NotificationAdapter):
    channel = "email"

    def send(self, subject: str, body: str, config: dict[str, Any]) -> None:
        api_key = config.get("sendgrid_api_key")
        to_email = config.get("to_email")
        from_email = config.get("from_email", "hackfind@localhost")
        if not api_key or not to_email:
            logger.warning("Email channel missing sendgrid_api_key/to_email; skipping")
            return

        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        }
        with httpx.Client(timeout=get_settings().http_timeout_seconds) as client:
            response = client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()


class TelegramNotifier(NotificationAdapter):
    channel = "telegram"

    def send(self, subject: str, body: str, config: dict[str, Any]) -> None:
        token = config.get("bot_token")
        chat_id = config.get("chat_id")
        if not token or not chat_id:
            logger.warning("Telegram channel missing bot_token/chat_id; skipping")
            return
        text = f"*{subject}*\n{body}"
        with httpx.Client(timeout=get_settings().http_timeout_seconds) as client:
            response = client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            )
            response.raise_for_status()


class SlackNotifier(NotificationAdapter):
    channel = "slack"

    def send(self, subject: str, body: str, config: dict[str, Any]) -> None:
        webhook = config.get("webhook_url")
        if not webhook:
            logger.warning("Slack channel missing webhook_url; skipping")
            return
        with httpx.Client(timeout=get_settings().http_timeout_seconds) as client:
            response = client.post(webhook, json={"text": f"*{subject}*\n{body}"})
            response.raise_for_status()


ADAPTERS: dict[str, NotificationAdapter] = {
    ConsoleNotifier.channel: ConsoleNotifier(),
    EmailNotifier.channel: EmailNotifier(),
    TelegramNotifier.channel: TelegramNotifier(),
    SlackNotifier.channel: SlackNotifier(),
}


def _format_new_matches(payload: dict[str, Any]) -> tuple[str, str]:
    matches = payload.get("matches") or []
    lines = [
        f"- {item.get('title')} ({item.get('source')}) score={item.get('score')}"
        for item in matches
    ]
    body = "New matched hackathons:\n" + ("\n".join(lines) if lines else "(none)")
    return "Hackfind: new matches", body


def _format_reminder(payload: dict[str, Any]) -> tuple[str, str]:
    days = payload.get("days_left")
    title = payload.get("title")
    url = payload.get("url")
    subject = f"Hackfind reminder: {title} ({days}d left)"
    body = f"{title}\nDeadline in {days} day(s)\n{url}"
    return subject, body


def dispatch(event: AgentEvent) -> None:
    if event.type == EVENT_NEW_MATCHES:
        subject, body = _format_new_matches(event.payload)
    elif event.type == EVENT_DEADLINE_REMINDER:
        subject, body = _format_reminder(event.payload)
    else:
        return

    with Session(engine) as session:
        channels = session.exec(
            select(NotificationChannel).where(NotificationChannel.enabled == True)  # noqa: E712
        ).all()
        if not channels:
            ADAPTERS["console"].send(subject, body, {})
            return

        for channel in channels:
            adapter = ADAPTERS.get(channel.channel)
            if not adapter:
                logger.warning("Unknown notification channel: %s", channel.channel)
                continue
            try:
                adapter.send(subject, body, channel.config or {})
            except Exception:  # noqa: BLE001
                logger.exception("Failed sending via %s", channel.channel)


_wired = False


def wire_notification_listeners() -> None:
    global _wired
    if _wired:
        return
    bus.on(EVENT_NEW_MATCHES, dispatch)
    bus.on(EVENT_DEADLINE_REMINDER, dispatch)
    _wired = True
