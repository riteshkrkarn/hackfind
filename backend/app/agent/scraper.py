from __future__ import annotations

import logging

from app.sources.registry import register_sources
from app.schemas.hackathon import Hackathon

logger = logging.getLogger(__name__)


class Scraper:
    def __init__(self, sources: list | None = None) -> None:
        self.sources = sources

    def fetch_all(self) -> list[Hackathon]:
        sources = self.sources if self.sources is not None else register_sources()
        collected: list[Hackathon] = []
        for source in sources:
            try:
                items = source.fetch()
                logger.info("Source %s returned %s items", source.name, len(items))
                collected.extend(items)
            except Exception:  # noqa: BLE001
                logger.exception("Source %s failed", source.name)
        unique: dict[str, Hackathon] = {}
        for item in collected:
            unique.setdefault(item.dedupe_key, item)
        return list(unique.values())
