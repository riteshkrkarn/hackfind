from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlmodel import Session, select

from app.config import get_settings
from app.db.models import CustomSource
from app.db.session import engine
from app.sources.base import SourceAdapter
from app.sources.definition import SourceDefinition
from app.sources.devfolio import DevfolioSource
from app.sources.devpost import DevpostSource
from app.sources.generic import GenericHtmlSource, GenericJsonSource
from app.sources.hackerearth import HackerEarthSource
from app.sources.mlh import MLHSource
from app.sources.seed import SeedSource
from app.sources.tavily import TavilySource

logger = logging.getLogger(__name__)

BUILTIN_FACTORIES: dict[str, type[SourceAdapter]] = {
    "devpost": DevpostSource,
    "devfolio": DevfolioSource,
    "mlh": MLHSource,
    "hackerearth": HackerEarthSource,
    "seed": SeedSource,
    "tavily": TavilySource,
}


def build_from_definition(definition: SourceDefinition) -> SourceAdapter | None:
    if not definition.enabled:
        return None

    if definition.kind == "html":
        return GenericHtmlSource(definition)
    if definition.kind == "json":
        return GenericJsonSource(definition)
    if definition.kind == "tavily":
        return TavilySource(definition)

    logger.warning("Unknown source kind: %s", definition.kind)
    return None


def _load_file_definitions() -> list[SourceDefinition]:
    settings = get_settings()
    path = Path(settings.sources_file)
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        logger.exception("Failed reading sources file %s", path)
        return []

    items = raw if isinstance(raw, list) else raw.get("sources", [])
    definitions: list[SourceDefinition] = []
    for item in items:
        try:
            definitions.append(SourceDefinition.model_validate(item))
        except Exception:  # noqa: BLE001
            logger.exception("Invalid source definition in file: %s", item)
    return definitions


def _load_db_definitions(session: Session | None = None) -> list[SourceDefinition]:
    owns = session is None
    session = session or Session(engine)
    try:
        rows = session.exec(
            select(CustomSource).where(CustomSource.enabled == True)  # noqa: E712
        ).all()
        return [
            SourceDefinition(
                name=row.name,
                kind=row.kind,  # type: ignore[arg-type]
                enabled=row.enabled,
                config=row.config or {},
            )
            for row in rows
        ]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Skipping DB custom sources (%s)", exc)
        return []
    finally:
        if owns:
            session.close()


def register_sources(session: Session | None = None) -> list[SourceAdapter]:
    """Built-ins + optional Tavily + file/DB generic sources."""
    settings = get_settings()
    enabled_builtins = {
        name.strip().lower()
        for name in settings.enabled_builtin_sources.split(",")
        if name.strip()
    }

    sources: list[SourceAdapter] = []
    seen_names: set[str] = set()

    def add(adapter: SourceAdapter | None) -> None:
        if adapter is None or adapter.name in seen_names:
            return
        sources.append(adapter)
        seen_names.add(adapter.name)

    if settings.use_seed_source and "seed" in enabled_builtins:
        add(SeedSource())

    for name, factory in BUILTIN_FACTORIES.items():
        if name in {"seed", "tavily"}:
            continue
        if name in enabled_builtins:
            add(factory())

    # Default Tavily source when API key is present (can also be added via DB/file)
    if settings.tavily_api_key and settings.tavily_enabled:
        add(TavilySource())

    for definition in _load_file_definitions() + _load_db_definitions(session):
        # Allow overriding a builtin by name via generic config
        if definition.name in seen_names and definition.kind in {"html", "json", "tavily"}:
            sources = [s for s in sources if s.name != definition.name]
            seen_names.discard(definition.name)
        add(build_from_definition(definition))

    return sources
