from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.agent.deadlines import DeadlineTracker
from app.agent.deduplication import DeduplicationService
from app.agent.events import EVENT_NEW_MATCHES, AgentEvent, bus
from app.agent.filters.engine import FilterEngine
from app.agent.scraper import Scraper
from app.db.models import HackathonRecord
from app.db.session import engine
from app.schemas.hackathon import Hackathon, HackathonStatus

logger = logging.getLogger(__name__)


def upsert_hackathons(session: Session, hackathons: list[Hackathon]) -> list[HackathonRecord]:
    saved: list[HackathonRecord] = []
    now = datetime.utcnow()
    for item in hackathons:
        existing = session.exec(
            select(HackathonRecord).where(HackathonRecord.dedupe_key == item.dedupe_key)
        ).first()
        if existing:
            existing.title = item.title
            existing.url = str(item.url)
            existing.description = item.description
            existing.mode = item.mode
            existing.location = item.location
            existing.starts_on = item.starts_on
            existing.ends_on = item.ends_on
            existing.apply_by = item.apply_by
            existing.prize_amount = item.prize_amount
            existing.team_size_min = item.team_size_min
            existing.team_size_max = item.team_size_max
            existing.tech_stack = item.tech_stack
            existing.domains = item.domains
            existing.last_seen_at = now
            saved.append(existing)
            continue

        record = HackathonRecord(
            external_id=item.external_id,
            source=item.source,
            dedupe_key=item.dedupe_key,
            title=item.title,
            url=str(item.url),
            description=item.description,
            mode=item.mode,
            location=item.location,
            starts_on=item.starts_on,
            ends_on=item.ends_on,
            apply_by=item.apply_by,
            prize_amount=item.prize_amount,
            team_size_min=item.team_size_min,
            team_size_max=item.team_size_max,
            tech_stack=item.tech_stack,
            domains=item.domains,
            status=HackathonStatus.new,
            first_seen_at=now,
            last_seen_at=now,
        )
        session.add(record)
        saved.append(record)

    session.commit()
    for record in saved:
        session.refresh(record)
    return saved


def run_agent_cycle(session: Session | None = None) -> dict[str, Any]:
    owns_session = session is None
    session = session or Session(engine)

    try:
        scraper = Scraper()
        dedupe = DeduplicationService(session)
        filters = FilterEngine(session)
        deadlines = DeadlineTracker(session)

        fetched = scraper.fetch_all()
        new_items = dedupe.filter_new(fetched)
        matched = filters.apply(new_items)

        # Persist all fetched (so Discover can browse), notify only new matches
        upsert_hackathons(session, fetched)
        dedupe.mark_seen(new_items)

        match_payload = [
            {
                "dedupe_key": item.hackathon.dedupe_key,
                "title": item.hackathon.title,
                "source": item.hackathon.source,
                "url": str(item.hackathon.url),
                "score": item.score,
                "matched_rules": item.matched_rules,
                "apply_by": item.hackathon.apply_by.isoformat()
                if item.hackathon.apply_by
                else None,
            }
            for item in matched
        ]
        if match_payload:
            bus.emit(AgentEvent(type=EVENT_NEW_MATCHES, payload={"matches": match_payload}))

        reminders = deadlines.run()

        result = {
            "fetched": len(fetched),
            "new": len(new_items),
            "matched": len(matched),
            "reminders": len(reminders),
            "matches": match_payload,
            "reminder_events": reminders,
        }
        logger.info("Agent cycle complete: %s", result)
        return result
    finally:
        if owns_session:
            session.close()
