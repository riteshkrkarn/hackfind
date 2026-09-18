from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Optional

import httpx

from app.config import get_settings
from app.schemas.hackathon import HackathonMode

logger = logging.getLogger(__name__)


def fetch_html(url: str) -> Optional[str]:
    settings = get_settings()
    try:
        with httpx.Client(
            timeout=settings.http_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text
    except Exception as exc:  # noqa: BLE001
        logger.warning("Fetch failed for %s: %s", url, exc)
        return None


def fetch_json(url: str) -> Optional[dict | list]:
    settings = get_settings()
    try:
        with httpx.Client(
            timeout=settings.http_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as exc:  # noqa: BLE001
        logger.warning("JSON fetch failed for %s: %s", url, exc)
        return None


def guess_mode(text: str) -> HackathonMode:
    lowered = text.lower()
    if "hybrid" in lowered:
        return HackathonMode.hybrid
    if "online" in lowered or "virtual" in lowered or "remote" in lowered:
        return HackathonMode.remote
    if "in-person" in lowered or "in person" in lowered or "onsite" in lowered:
        return HackathonMode.in_person
    return HackathonMode.unknown


def slug_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or datetime.utcnow().strftime("%Y%m%d%H%M%S")
