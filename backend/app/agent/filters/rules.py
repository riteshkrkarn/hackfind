from __future__ import annotations

from dataclasses import dataclass

from app.db.models import FilterProfile
from app.schemas.hackathon import Hackathon


@dataclass
class ScoredHackathon:
    hackathon: Hackathon
    score: float
    matched_rules: list[str]


class FilterRule:
    name: str

    def score(self, hackathon: Hackathon, profile: FilterProfile) -> tuple[float, bool]:
        """Return (score_delta, hard_fail). hard_fail drops the hackathon."""
        raise NotImplementedError


class TechStackRule(FilterRule):
    name = "tech_stack"

    def score(self, hackathon: Hackathon, profile: FilterProfile) -> tuple[float, bool]:
        wanted = {item.lower() for item in profile.tech_stack or []}
        if not wanted:
            return 0.0, False
        have = {item.lower() for item in hackathon.tech_stack}
        overlap = wanted & have
        if not overlap:
            return 0.0, True
        return float(len(overlap)) * 2.0, False


class ModeRule(FilterRule):
    name = "mode"

    def score(self, hackathon: Hackathon, profile: FilterProfile) -> tuple[float, bool]:
        wanted = {item.lower() for item in profile.modes or []}
        if not wanted:
            return 0.0, False
        if hackathon.mode.value not in wanted and "unknown" not in wanted:
            return 0.0, True
        return 1.5, False


class DomainRule(FilterRule):
    name = "domain"

    def score(self, hackathon: Hackathon, profile: FilterProfile) -> tuple[float, bool]:
        wanted = {item.lower() for item in profile.domains or []}
        if not wanted:
            return 0.0, False
        have = {item.lower() for item in hackathon.domains}
        overlap = wanted & have
        if not overlap:
            return 0.0, True
        return float(len(overlap)) * 2.5, False


class PrizeRangeRule(FilterRule):
    name = "prize_range"

    def score(self, hackathon: Hackathon, profile: FilterProfile) -> tuple[float, bool]:
        if profile.min_prize is None and profile.max_prize is None:
            return 0.0, False
        if hackathon.prize_amount is None:
            return 0.0, False
        if profile.min_prize is not None and hackathon.prize_amount < profile.min_prize:
            return 0.0, True
        if profile.max_prize is not None and hackathon.prize_amount > profile.max_prize:
            return 0.0, True
        return 1.0, False


class TeamSizeRule(FilterRule):
    name = "team_size"

    def score(self, hackathon: Hackathon, profile: FilterProfile) -> tuple[float, bool]:
        if profile.team_size_min is None and profile.team_size_max is None:
            return 0.0, False

        # Overlap check between preferred range and event range
        event_min = hackathon.team_size_min or 1
        event_max = hackathon.team_size_max or event_min
        pref_min = profile.team_size_min or event_min
        pref_max = profile.team_size_max or event_max
        overlaps = event_min <= pref_max and pref_min <= event_max
        if not overlaps:
            return 0.0, True
        return 1.0, False


DEFAULT_RULES: list[FilterRule] = [
    TechStackRule(),
    ModeRule(),
    DomainRule(),
    PrizeRangeRule(),
    TeamSizeRule(),
]
