from __future__ import annotations

from datetime import date, datetime

from sqlmodel import Session, select

from app.agent.events import EVENT_DEADLINE_REMINDER, AgentEvent, bus
from app.db.models import HackathonRecord, NotificationChannel, ReminderLog
from app.schemas.hackathon import HackathonStatus


class DeadlineTracker:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _thresholds(self) -> list[int]:
        channels = self.session.exec(
            select(NotificationChannel).where(NotificationChannel.enabled == True)  # noqa: E712
        ).all()
        if not channels:
            return [7, 1, 0]
        values: set[int] = set()
        for channel in channels:
            values.update(channel.reminder_thresholds_days or [7, 1, 0])
        return sorted(values, reverse=True)

    def run(self) -> list[dict]:
        today = date.today()
        thresholds = self._thresholds()
        watched = self.session.exec(
            select(HackathonRecord).where(
                HackathonRecord.status.in_(
                    [HackathonStatus.interested, HackathonStatus.joined]
                )
            )
        ).all()

        emitted: list[dict] = []
        for record in watched:
            if not record.apply_by:
                continue
            days_left = (record.apply_by - today).days
            if days_left < 0:
                continue
            if days_left not in thresholds:
                continue

            already = self.session.exec(
                select(ReminderLog).where(
                    ReminderLog.hackathon_id == record.id,
                    ReminderLog.threshold_days == days_left,
                )
            ).first()
            if already:
                continue

            payload = {
                "hackathon_id": record.id,
                "title": record.title,
                "url": record.url,
                "apply_by": record.apply_by.isoformat(),
                "days_left": days_left,
                "status": record.status.value,
            }
            bus.emit(AgentEvent(type=EVENT_DEADLINE_REMINDER, payload=payload))
            self.session.add(
                ReminderLog(
                    hackathon_id=record.id,
                    threshold_days=days_left,
                    sent_at=datetime.utcnow(),
                )
            )
            emitted.append(payload)

        self.session.commit()
        return emitted
