from __future__ import annotations

import logging
import re
from datetime import date
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.schemas.hackathon import Hackathon
from app.sources.base import SourceAdapter
from app.sources.http_utils import fetch_html, slug_id
from app.sources.parsing import mode_from_location, parse_mlh_link_text

logger = logging.getLogger(__name__)


class MLHSource(SourceAdapter):
    name = "mlh"

    def _season_urls(self) -> list[str]:
        year = date.today().year
        return [
            f"https://mlh.io/seasons/{year}/events",
            f"https://mlh.io/seasons/{year + 1}/events",
            "https://mlh.io/events",
        ]

    def fetch(self) -> list[Hackathon]:
        results: list[Hackathon] = []
        seen: set[str] = set()

        for list_url in self._season_urls():
            html = fetch_html(list_url)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.select("a[href]"):
                href = link.get("href") or ""
                if "events.mlh.io/events/" not in href and "/events/" not in href:
                    continue
                if any(skip in href for skip in ("/prizes", "/seasons/", "utm_content=nav")):
                    continue

                absolute = urljoin(list_url, href)
                parsed = urlparse(absolute)
                if "events.mlh.io" not in parsed.netloc:
                    continue

                text = link.get_text(" ", strip=True)
                if len(text) < 8:
                    continue
                if text.lower() in {"upcoming hackathons", "prizes & freebies"}:
                    continue

                path = parsed.path.rstrip("/")
                slug = path.split("/")[-1]
                # events.mlh.io slugs look like 14302-global-hack-week-hacking-for-good
                slug_title = re.sub(
                    r"^\d+-",
                    "",
                    slug,
                ).replace("-", " ").strip()
                title_from_text, location, starts, ends = parse_mlh_link_text(text)
                title = slug_title.title() if slug_title else title_from_text
                external = slug_id(slug or title)
                if external in seen:
                    continue
                seen.add(external)

                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                results.append(
                    Hackathon(
                        external_id=external,
                        source=self.name,
                        title=title[:160],
                        url=clean_url,
                        mode=mode_from_location(location or text, text),
                        location=location,
                        starts_on=starts,
                        ends_on=ends,
                        apply_by=starts,
                    )
                )

        logger.info("MLH fetched %s hackathons", len(results))
        return results
