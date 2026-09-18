from abc import ABC, abstractmethod

from app.schemas.hackathon import Hackathon


class SourceAdapter(ABC):
    """Common interface for every platform adapter."""

    name: str

    @abstractmethod
    def fetch(self) -> list[Hackathon]:
        """Return normalized hackathons from this source."""


def register_sources():
    from app.sources.registry import register_sources as _register

    return _register()
