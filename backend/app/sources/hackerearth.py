from __future__ import annotations

import json
import logging
import re
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.schemas.hackathon import Hackathon
from app.sources.base import SourceAdapter
from app.sources.http_utils import fetch_html, guess_mode, slug_id
from app.sources.parsing import parse_iso_date

logger = logging.getLogger(__name__)


class HackerEarthSource(SourceAdapter):
    name = "hackerearth"
    list_url = "https://www.hackerearth.com/challenges/hackathon/"

    def _from_next_data(self, html: str) -> list[Hackathon]:
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script or not script.string:
            return []
        try:
            payload = json.loads(script.string)
        except json.JSONDecodeError:
            return []

        # Walk the blob for challenge-like dicts
        found: list[dict[str, Any]] = []

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                keys = {k.lower() for k in node.keys()}
                if {"title", "url"} <= keys or {"title", "slug"} <= keys:
                    title = str(node.get("title") or node.get("name") or "")
                    if "hackathon" in title.lower() or node.get("challenge_type") == "hackathon":
                        found.append(node)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(payload)
        results: list[Hackathon] = []
        seen: set[str] = set()
        for item in found:
            title = str(item.get("title") or item.get("name") or "").strip()
            url = str(item.get("url") or item.get("challenge_url") or "").strip()
            slug = str(item.get("slug") or "").strip()
            if not url and slug:
                url = urljoin("https://www.hackerearth.com/challenges/hackathon/", f"{slug}/")
            if not title or not url:
                continue
            external = slug_id(str(item.get("id") or slug or url))
            if external in seen:
                continue
            seen.add(external)
            results.append(
                Hackathon(
                    external_id=external,
                    source=self.name,
                    title=title[:160],
                    url=url if url.startswith("http") else urljoin("https://www.hackerearth.com", url),
                    description=str(item.get("description") or "")[:400] or None,
                    mode=guess_mode(f"{title} {item.get('location') or ''}"),
                    starts_on=parse_iso_date(str(item.get("start_date") or item.get("starts_at") or "")),
                    ends_on=parse_iso_date(str(item.get("end_date") or item.get("ends_at") or "")),
                    apply_by=parse_iso_date(str(item.get("registration_end") or "")),
                )
            )
        return results

    def _from_anchors(self, html: str) -> list[Hackathon]:
        soup = BeautifulSoup(html, "html.parser")
        results: list[Hackathon] = []
        seen: set[str] = set()
        for link in soup.select("a[href*='hackathon']"):
            href = link.get("href") or ""
            title = link.get_text(" ", strip=True)
            if len(title) < 8:
                continue
            if any(token in href.lower() for token in ("login", "register", "recruit")):
                continue
            path_ok = bool(re.search(r"/challenges/hackathon/[^/]+/?", href))
            if not path_ok:
                continue
            url = urljoin("https://www.hackerearth.com", href)
            external = slug_id(url.rstrip("/").split("/")[-1] or title)
            if external in seen:
                continue
            seen.add(external)
            results.append(
                Hackathon(
                    external_id=external,
                    source=self.name,
                    title=title[:160],
                    url=url,
                    mode=guess_mode(title),
                )
            )
        return results

    def fetch(self) -> list[Hackathon]:
        html = fetch_html(self.list_url)
        if not html:
            return []

        results = self._from_next_data(html)
        if not results:
            results = self._from_anchors(html)

        logger.info("HackerEarth fetched %s hackathons", len(results))
        return results
