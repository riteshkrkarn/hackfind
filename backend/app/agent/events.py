from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AgentEvent:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)


Listener = Callable[[AgentEvent], None]


class EventBus:
    """In-process event bus. Swap later for Redis/BullMQ if volume grows."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Listener]] = {}

    def on(self, event_type: str, listener: Listener) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def emit(self, event: AgentEvent) -> None:
        listeners = self._listeners.get(event.type, []) + self._listeners.get("*", [])
        for listener in listeners:
            try:
                listener(event)
            except Exception:  # noqa: BLE001
                logger.exception("Listener failed for event %s", event.type)


bus = EventBus()

EVENT_NEW_MATCHES = "hackathons.new_matches"
EVENT_DEADLINE_REMINDER = "deadlines.reminder"
