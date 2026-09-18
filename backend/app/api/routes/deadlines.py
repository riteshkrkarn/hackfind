from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.api.schemas import DeadlineOut
from app.db.models import HackathonRecord
from app.db.session import get_session
from app.schemas.hackathon import HackathonStatus

router = APIRouter(prefix="/deadlines", tags=["deadlines"])


@router.get("", response_model=list[DeadlineOut])
def list_deadlines(
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
) -> list[DeadlineOut]:
    today = date.today()
    rows = session.exec(
        select(HackathonRecord)
        .where(
            HackathonRecord.status.in_(
                [HackathonStatus.interested, HackathonStatus.joined]
            )
        )
        .where(HackathonRecord.apply_by.is_not(None))
        .order_by(HackathonRecord.apply_by)
        .limit(limit)
    ).all()

    results: list[DeadlineOut] = []
    for row in rows:
        if not row.apply_by:
            continue
        results.append(
            DeadlineOut(
                hackathon_id=row.id,
                title=row.title,
                url=row.url,
                status=row.status,
                apply_by=row.apply_by.isoformat(),
                days_left=(row.apply_by - today).days,
            )
        )
    return results
