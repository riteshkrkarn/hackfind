from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, select

from app.api.schemas import HackathonOut, StatusUpdate, record_to_out
from app.db.models import HackathonRecord
from app.db.session import get_session
from app.schemas.hackathon import HackathonStatus

router = APIRouter(prefix="/hackathons", tags=["hackathons"])


@router.get("", response_model=list[HackathonOut])
def list_hackathons(
    status: HackathonStatus | None = None,
    source: str | None = None,
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[HackathonOut]:
    statement = select(HackathonRecord).order_by(
        # Keep offline seed samples, but don't bury real scrapes under them
        col(HackathonRecord.source) == "seed",
        col(HackathonRecord.last_seen_at).desc(),
    )
    if status:
        statement = statement.where(HackathonRecord.status == status)
    if source:
        statement = statement.where(HackathonRecord.source == source)
    if q:
        statement = statement.where(col(HackathonRecord.title).contains(q))
    rows = session.exec(statement.offset(offset).limit(limit)).all()
    return [record_to_out(row) for row in rows]


@router.post("/{hackathon_id}/status", response_model=HackathonOut)
def update_status(
    hackathon_id: int,
    body: StatusUpdate,
    session: Session = Depends(get_session),
) -> HackathonOut:
    record = session.get(HackathonRecord, hackathon_id)
    if not record:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    record.status = body.status
    session.add(record)
    session.commit()
    session.refresh(record)
    return record_to_out(record)
