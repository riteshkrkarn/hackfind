from __future__ import annotations

import logging
from urllib.parse import urlparse

import httpx

from app.config import get_settings
from app.schemas.hackathon import Hackathon
from app.sources.base import SourceAdapter
from app.sources.definition import SourceDefinition, TavilySourceConfig
from app.sources.http_utils import guess_mode, slug_id

logger = logging.getLogger(__name__)


class TavilySource(SourceAdapter):
    """Discover hackathons via Tavily web search (good free-tier limits)."""

    def __init__(self, definition: SourceDefinition | None = None) -> None:
        if definition is None:
            self.name = "tavily"
            self.cfg = TavilySourceConfig()
        else:
            self.name = definition.name
            self.cfg = TavilySourceConfig.model_validate(definition.config)

    def fetch(self) -> list[Hackathon]:
        settings = get_settings()
        api_key = settings.tavily_api_key
        if not api_key:
            logger.info("Tavily skipped: TAVILY_API_KEY not set")
            return []

        body: dict = {
            "api_key": api_key,
            "query": self.cfg.query,
            "search_depth": self.cfg.search_depth,
            "max_results": self.cfg.max_results,
            "include_answer": False,
            "topic": self.cfg.topic,
        }
        if self.cfg.include_domains:
            body["include_domains"] = self.cfg.include_domains

        try:
            with httpx.Client(timeout=settings.http_timeout_seconds) as client:
                response = client.post("https://api.tavily.com/search", json=body)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Tavily search failed: %s", exc)
            return []

        results: list[Hackathon] = []
        for item in data.get("results") or []:
            url = (item.get("url") or "").strip()
            title = (item.get("title") or "").strip()
            content = (item.get("content") or "").strip()
            if not url or not title:
                continue
            # Prefer results that look hackathon-related
            blob = f"{title} {content}".lower()
            if "hackathon" not in blob and "hackathon" not in url.lower():
                continue
            host = urlparse(url).netloc.replace("www.", "")
            results.append(
                Hackathon(
                    external_id=slug_id(f"{host}-{title}"),
                    source=self.name,
                    title=title[:160],
                    url=url,
                    description=content[:400] or None,
                    mode=guess_mode(blob),
                )
            )

        logger.info("Tavily source %s fetched %s", self.name, len(results))
        return results
