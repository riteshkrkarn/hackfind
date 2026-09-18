from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import get_settings
from app.schemas.hackathon import Hackathon, HackathonMode
from app.sources.base import SourceAdapter
from app.sources.http_utils import slug_id
from app.sources.parsing import mode_from_location, parse_iso_date

logger = logging.getLogger(__name__)


class DevfolioSource(SourceAdapter):
    name = "devfolio"
    api_url = "https://api.devfolio.co/api/hackathons"

    def _get_page(self, client: httpx.Client, filt: str, page: int) -> list[dict[str, Any]]:
        response = client.get(
            self.api_url,
            params={"filter": filt, "page": page, "limit": 20},
        )
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("result") or []
        return rows if isinstance(rows, list) else []

    def fetch(self) -> list[Hackathon]:
        settings = get_settings()
        results: list[Hackathon] = []
        seen: set[str] = set()

        try:
            with httpx.Client(
                timeout=settings.http_timeout_seconds,
                headers={
                    "User-Agent": settings.user_agent,
                    "Accept": "application/json",
                },
                follow_redirects=True,
            ) as client:
                for filt in ("application_open", "upcoming", "live"):
                    for page in (1, 2):
                        try:
                            rows = self._get_page(client, filt, page)
                        except Exception as exc:  # noqa: BLE001
                            logger.warning("Devfolio filter=%s page=%s failed: %s", filt, page, exc)
                            break
                        if not rows:
                            break
                        for item in rows:
                            uuid = str(item.get("uuid") or item.get("slug") or "")
                            if not uuid or uuid in seen:
                                continue
                            seen.add(uuid)
                            title = (item.get("name") or "").strip()
                            slug = (item.get("slug") or uuid).strip()
                            if not title:
                                continue
                            url = f"https://devfolio.co/hackathons/{slug}"
                            is_online = bool(item.get("is_online") or item.get("online"))
                            location = item.get("location") or item.get("city")
                            mode = (
                                HackathonMode.remote
                                if is_online
                                else mode_from_location(location, title)
                            )
                            starts = parse_iso_date(item.get("starts_at"))
                            ends = parse_iso_date(item.get("ends_at"))
                            apply_by = parse_iso_date(
                                item.get("hackathon_setting", {}).get("reg_ends_at")
                                if isinstance(item.get("hackathon_setting"), dict)
                                else item.get("application_ends_at")
                            ) or starts
                            results.append(
                                Hackathon(
                                    external_id=slug_id(uuid),
                                    source=self.name,
                                    title=title[:160],
                                    url=url,
                                    description=(item.get("desc") or item.get("tagline") or None),
                                    mode=mode,
                                    location=location,
                                    starts_on=starts,
                                    ends_on=ends,
                                    apply_by=apply_by,
                                    domains=[],
                                    tech_stack=[],
                                )
                            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Devfolio API failed: %s", exc)
            return []

        logger.info("Devfolio fetched %s hackathons", len(results))
        return results
