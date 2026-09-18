from __future__ import annotations

import logging
import re
from datetime import date, datetime
from typing import Optional

from app.schemas.hackathon import HackathonMode

logger = logging.getLogger(__name__)

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def parse_iso_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def parse_prize_amount(raw: Optional[str]) -> Optional[int]:
    if not raw:
        return None
    text = re.sub(r"<[^>]+>", "", str(raw))
    text = text.replace(",", "").replace("$", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*([kmb])?", text, flags=re.I)
    if not match:
        digits = re.findall(r"\d+", text)
        return int(digits[0]) if digits else None
    amount = float(match.group(1))
    suffix = (match.group(2) or "").lower()
    if suffix == "k":
        amount *= 1_000
    elif suffix == "m":
        amount *= 1_000_000
    elif suffix == "b":
        amount *= 1_000_000_000
    return int(amount)


def parse_devpost_period(period: Optional[str]) -> tuple[Optional[date], Optional[date]]:
    """Parse strings like 'Jul 31 - Oct 01, 2026'."""
    if not period:
        return None, None
    match = re.search(
        r"([A-Za-z]+)\s+(\d{1,2})\s*[-–]\s*([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})",
        period,
    )
    if not match:
        return None, None
    m1, d1, m2, d2, year = match.groups()
    start_month = MONTHS.get(m1.lower())
    end_month = MONTHS.get(m2.lower())
    if not start_month or not end_month:
        return None, None
    year_i = int(year)
    start_year = year_i if start_month <= end_month else year_i - 1
    try:
        return (
            date(start_year, start_month, int(d1)),
            date(year_i, end_month, int(d2)),
        )
    except ValueError:
        return None, None


def parse_mlh_link_text(text: str) -> tuple[str, Optional[str], Optional[date], Optional[date]]:
    """
    MLH season cards often concatenate location + title + date range, e.g.
    'Davis , California HackDavis 2026 Hackathon MAY 09 - 10 Davis...'
    """
    cleaned = re.sub(r"\s+", " ", text).strip()
    date_match = re.search(
        r"([A-Z]{3,9})\s+(\d{1,2})\s*[-–]\s*(\d{1,2})(?:\s*,?\s*(\d{4}))?",
        cleaned,
        flags=re.I,
    )
    starts = ends = None
    title = cleaned
    location = None
    if date_match:
        month = MONTHS.get(date_match.group(1).lower())
        d1 = int(date_match.group(2))
        d2 = int(date_match.group(3))
        year = int(date_match.group(4) or date.today().year)
        if month:
            try:
                starts = date(year, month, d1)
                ends = date(year, month, d2)
            except ValueError:
                starts = ends = None
        title = cleaned[: date_match.start()].strip(" ,-") or cleaned

    # Prefer a trailing location fragment after the title-ish words
    loc_match = re.search(
        r"\b([A-Z][a-zA-Z]+(?:[\s,]+[A-Z][a-zA-Z]+){0,3})\s*$",
        title,
    )
    if loc_match and len(loc_match.group(1)) < 40:
        location = loc_match.group(1)

    return title[:160], location, starts, ends


def mode_from_location(location: Optional[str], fallback_text: str = "") -> HackathonMode:
    blob = f"{location or ''} {fallback_text}".lower()
    if "online" in blob or "virtual" in blob or "remote" in blob or "everywhere" in blob:
        return HackathonMode.remote
    if "hybrid" in blob:
        return HackathonMode.hybrid
    if location:
        return HackathonMode.in_person
    return HackathonMode.unknown
