from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.schemas import NotificationChannelIn, NotificationChannelOut
from app.db.models import NotificationChannel
from app.db.session import get_session

router = APIRouter(prefix="/notifications", tags=["notifications"])


def to_out(channel: NotificationChannel) -> NotificationChannelOut:
    return NotificationChannelOut(
        id=channel.id,
        channel=channel.channel,
        enabled=channel.enabled,
        config=channel.config or {},
        reminder_thresholds_days=channel.reminder_thresholds_days or [7, 1, 0],
        created_at=channel.created_at,
        updated_at=channel.updated_at,
    )


@router.get("", response_model=list[NotificationChannelOut])
def list_channels(session: Session = Depends(get_session)) -> list[NotificationChannelOut]:
    rows = session.exec(select(NotificationChannel).order_by(NotificationChannel.id)).all()
    return [to_out(row) for row in rows]


@router.post("", response_model=NotificationChannelOut, status_code=201)
def create_channel(
    body: NotificationChannelIn,
    session: Session = Depends(get_session),
) -> NotificationChannelOut:
    channel = NotificationChannel(**body.model_dump())
    session.add(channel)
    session.commit()
    session.refresh(channel)
    return to_out(channel)


@router.put("/{channel_id}", response_model=NotificationChannelOut)
def update_channel(
    channel_id: int,
    body: NotificationChannelIn,
    session: Session = Depends(get_session),
) -> NotificationChannelOut:
    channel = session.get(NotificationChannel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Notification channel not found")
    for key, value in body.model_dump().items():
        setattr(channel, key, value)
    channel.updated_at = datetime.utcnow()
    session.add(channel)
    session.commit()
    session.refresh(channel)
    return to_out(channel)


@router.delete("/{channel_id}", status_code=204)
def delete_channel(channel_id: int, session: Session = Depends(get_session)) -> None:
    channel = session.get(NotificationChannel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Notification channel not found")
    session.delete(channel)
    session.commit()
