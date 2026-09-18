from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class HackathonMode(str, Enum):
    remote = "remote"
    in_person = "in_person"
    hybrid = "hybrid"
    unknown = "unknown"


class HackathonStatus(str, Enum):
    new = "new"
    interested = "interested"
    joined = "joined"
    ignored = "ignored"


class Hackathon(BaseModel):
    """Normalized hackathon shared across sources, agent, API, and UI."""

    external_id: str = Field(..., description="Stable id within the source platform")
    source: str
    title: str
    url: HttpUrl | str
    description: Optional[str] = None
    mode: HackathonMode = HackathonMode.unknown
    location: Optional[str] = None
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    apply_by: Optional[date] = None
    prize_amount: Optional[int] = Field(
        default=None, description="Total prize pool in USD when known"
    )
    team_size_min: Optional[int] = None
    team_size_max: Optional[int] = None
    tech_stack: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def dedupe_key(self) -> str:
        return f"{self.source}:{self.external_id}".lower()
