from collections.abc import Generator
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.db.models import (
    FilterProfile,
    HackathonRecord,
    NotificationChannel,
)
from app.db.session import get_session
from app.schemas.hackathon import HackathonMode, HackathonStatus


class HackathonOut(BaseModel):
    id: int
    external_id: str
    source: str
    title: str
    url: str
    description: Optional[str] = None
    mode: HackathonMode
    location: Optional[str] = None
    starts_on: Optional[str] = None
    ends_on: Optional[str] = None
    apply_by: Optional[str] = None
    prize_amount: Optional[int] = None
    team_size_min: Optional[int] = None
    team_size_max: Optional[int] = None
    tech_stack: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    status: HackathonStatus
    first_seen_at: datetime
    last_seen_at: datetime


class StatusUpdate(BaseModel):
    status: HackathonStatus


class FilterProfileIn(BaseModel):
    name: str
    active: bool = True
    tech_stack: list[str] = Field(default_factory=list)
    modes: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    min_prize: Optional[int] = None
    max_prize: Optional[int] = None
    team_size_min: Optional[int] = None
    team_size_max: Optional[int] = None


class FilterProfileOut(FilterProfileIn):
    id: int
    created_at: datetime
    updated_at: datetime


class NotificationChannelIn(BaseModel):
    channel: str
    enabled: bool = True
    config: dict = Field(default_factory=dict)
    reminder_thresholds_days: list[int] = Field(default_factory=lambda: [7, 1, 0])


class NotificationChannelOut(NotificationChannelIn):
    id: int
    created_at: datetime
    updated_at: datetime


class DeadlineOut(BaseModel):
    hackathon_id: int
    title: str
    url: str
    status: HackathonStatus
    apply_by: str
    days_left: int


def record_to_out(record: HackathonRecord) -> HackathonOut:
    return HackathonOut(
        id=record.id,
        external_id=record.external_id,
        source=record.source,
        title=record.title,
        url=record.url,
        description=record.description,
        mode=record.mode,
        location=record.location,
        starts_on=record.starts_on.isoformat() if record.starts_on else None,
        ends_on=record.ends_on.isoformat() if record.ends_on else None,
        apply_by=record.apply_by.isoformat() if record.apply_by else None,
        prize_amount=record.prize_amount,
        team_size_min=record.team_size_min,
        team_size_max=record.team_size_max,
        tech_stack=record.tech_stack or [],
        domains=record.domains or [],
        status=record.status,
        first_seen_at=record.first_seen_at,
        last_seen_at=record.last_seen_at,
    )


SessionDep = Depends(get_session)
