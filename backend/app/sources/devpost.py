from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.schemas.hackathon import Hackathon
from app.sources.base import SourceAdapter
from app.sources.http_utils import fetch_html, guess_mode, slug_id
from app.sources.parsing import (
    mode_from_location,
    parse_devpost_period,
    parse_prize_amount,
)

__all__ = ["DevpostSource", "fetch_html", "guess_mode", "slug_id"]

logger = logging.getLogger(__name__)


class DevpostSource(SourceAdapter):
    name = "devpost"
    api_url = "https://devpost.com/api/hackathons"

    def fetch(self) -> list[Hackathon]:
        settings = get_settings()
        params = [
            ("status[]", "upcoming"),
            ("status[]", "open"),
            ("per_page", "50"),
            ("page", "1"),
        ]
        try:
            with httpx.Client(
                timeout=settings.http_timeout_seconds,
                headers={
                    "User-Agent": settings.user_agent,
                    "Accept": "application/json",
                },
                follow_redirects=True,
            ) as client:
                response = client.get(self.api_url, params=params)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Devpost API failed: %s", exc)
            return []

        results: list[Hackathon] = []
        for item in payload.get("hackathons") or []:
            title = (item.get("title") or "").strip()
            url = (item.get("url") or "").strip()
            if not title or not url:
                continue
            location_info = item.get("displayed_location") or {}
            location = location_info.get("location")
            starts, ends = parse_devpost_period(item.get("submission_period_dates"))
            themes = [
                theme.get("name")
                for theme in (item.get("themes") or [])
                if isinstance(theme, dict) and theme.get("name")
            ]
            results.append(
                Hackathon(
                    external_id=str(item.get("id") or slug_id(url)),
                    source=self.name,
                    title=title[:160],
                    url=url,
                    description=(item.get("organization_name") or None),
                    mode=mode_from_location(location, title),
                    location=location,
                    starts_on=starts,
                    ends_on=ends,
                    apply_by=ends,
                    prize_amount=parse_prize_amount(item.get("prize_amount")),
                    domains=[str(t).lower() for t in themes],
                    tech_stack=[],
                )
            )

        logger.info("Devpost fetched %s hackathons", len(results))
        return results
