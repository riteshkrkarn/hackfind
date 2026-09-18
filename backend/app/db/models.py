from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from app.schemas.hackathon import HackathonMode, HackathonStatus


class HackathonRecord(SQLModel, table=True):
    __tablename__ = "hackathons"

    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(index=True)
    source: str = Field(index=True)
    dedupe_key: str = Field(index=True, unique=True)
    title: str
    url: str
    description: Optional[str] = None
    mode: HackathonMode = HackathonMode.unknown
    location: Optional[str] = None
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    apply_by: Optional[date] = Field(default=None, index=True)
    prize_amount: Optional[int] = None
    team_size_min: Optional[int] = None
    team_size_max: Optional[int] = None
    tech_stack: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    domains: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: HackathonStatus = Field(default=HackathonStatus.new, index=True)
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)


class SeenHash(SQLModel, table=True):
    __tablename__ = "seen_hashes"

    dedupe_key: str = Field(primary_key=True)
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)


class FilterProfile(SQLModel, table=True):
    __tablename__ = "filter_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    active: bool = True
    tech_stack: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    modes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    domains: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    min_prize: Optional[int] = None
    max_prize: Optional[int] = None
    team_size_min: Optional[int] = None
    team_size_max: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationChannel(SQLModel, table=True):
    __tablename__ = "notification_channels"

    id: Optional[int] = Field(default=None, primary_key=True)
    channel: str = Field(index=True)  # email | telegram | slack | console
    enabled: bool = True
    # Credentials/config stored as JSON so dashboard can update without env edits
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))
    reminder_thresholds_days: list[int] = Field(
        default_factory=lambda: [7, 1, 0],
        sa_column=Column(JSON),
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReminderLog(SQLModel, table=True):
    __tablename__ = "reminder_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    hackathon_id: int = Field(index=True)
    threshold_days: int
    sent_at: datetime = Field(default_factory=datetime.utcnow)


class CustomSource(SQLModel, table=True):
    """User/config-defined sources (html | json | tavily) — no new code file needed."""

    __tablename__ = "custom_sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    kind: str = Field(index=True)  # html | json | tavily
    enabled: bool = True
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
