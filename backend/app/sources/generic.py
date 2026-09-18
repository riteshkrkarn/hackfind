from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.schemas.hackathon import Hackathon
from app.sources.base import SourceAdapter
from app.sources.definition import HtmlSourceConfig, JsonSourceConfig, SourceDefinition
from app.sources.http_utils import fetch_html, fetch_json, guess_mode, slug_id

logger = logging.getLogger(__name__)


def _dig(data: Any, path: str) -> Any:
    if not path:
        return data
    current = data
    for part in path.split("."):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            current = current[idx] if idx < len(current) else None
        else:
            return None
    return current


class GenericHtmlSource(SourceAdapter):
    """Scrape any listing page from selectors — for new platforms without a dedicated adapter."""

    def __init__(self, definition: SourceDefinition) -> None:
        self.name = definition.name
        self.cfg = HtmlSourceConfig.model_validate(definition.config)

    def fetch(self) -> list[Hackathon]:
        html = fetch_html(self.cfg.list_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        base = self.cfg.base_url or f"{urlparse(self.cfg.list_url).scheme}://{urlparse(self.cfg.list_url).netloc}"
        results: list[Hackathon] = []

        for node in soup.select(self.cfg.link_selector)[: self.cfg.max_items * 2]:
            href = node.get("href") if node.name == "a" else None
            if not href and node.name != "a":
                link = node.select_one("a[href]")
                href = link.get("href") if link else None
                title_node = (
                    node.select_one(self.cfg.title_selector)
                    if self.cfg.title_selector
                    else (link or node)
                )
            else:
                title_node = (
                    node.select_one(self.cfg.title_selector)
                    if self.cfg.title_selector
                    else node
                )

            if not href:
                continue
            title = title_node.get_text(strip=True) if title_node is not None else ""
            if len(title) < self.cfg.min_title_length:
                continue

            lowered = f"{href} {title}".lower()
            if any(token in lowered for token in self.cfg.skip_substrings):
                continue

            url = urljoin(base, href)
            path = urlparse(url).path
            results.append(
                Hackathon(
                    external_id=slug_id(path or title),
                    source=self.name,
                    title=title[:160],
                    url=url,
                    mode=guess_mode(title),
                )
            )
            if len(results) >= self.cfg.max_items:
                break

        unique = {item.external_id: item for item in results}
        logger.info("Generic HTML source %s fetched %s", self.name, len(unique))
        return list(unique.values())


class GenericJsonSource(SourceAdapter):
    """Pull hackathons from any JSON API with field mapping."""

    def __init__(self, definition: SourceDefinition) -> None:
        self.name = definition.name
        self.cfg = JsonSourceConfig.model_validate(definition.config)

    def fetch(self) -> list[Hackathon]:
        payload = fetch_json(self.cfg.list_url)
        if payload is None:
            return []

        items = _dig(payload, self.cfg.items_path)
        if not isinstance(items, list):
            logger.warning("JSON source %s: items_path did not resolve to a list", self.name)
            return []

        results: list[Hackathon] = []
        for raw in items[: self.cfg.max_items]:
            if not isinstance(raw, dict):
                continue
            title = str(raw.get(self.cfg.title_key) or "").strip()
            url = str(raw.get(self.cfg.url_key) or "").strip()
            if not title or not url:
                continue
            external = raw.get(self.cfg.id_key) if self.cfg.id_key else None
            description = None
            if self.cfg.description_key:
                value = raw.get(self.cfg.description_key)
                description = str(value)[:400] if value else None
            results.append(
                Hackathon(
                    external_id=slug_id(str(external or url)),
                    source=self.name,
                    title=title[:160],
                    url=url,
                    description=description,
                    mode=guess_mode(f"{title} {description or ''}"),
                )
            )

        logger.info("Generic JSON source %s fetched %s", self.name, len(results))
        return results
