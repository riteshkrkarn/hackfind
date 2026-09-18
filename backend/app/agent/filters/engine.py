from sqlmodel import Session, select

from app.agent.filters.rules import DEFAULT_RULES, FilterRule, ScoredHackathon
from app.db.models import FilterProfile
from app.schemas.hackathon import Hackathon


class FilterEngine:
    def __init__(self, session: Session, rules: list[FilterRule] | None = None) -> None:
        self.session = session
        self.rules = rules or DEFAULT_RULES

    def active_profiles(self) -> list[FilterProfile]:
        return list(
            self.session.exec(select(FilterProfile).where(FilterProfile.active == True)).all()  # noqa: E712
        )

    def apply(
        self,
        hackathons: list[Hackathon],
        profiles: list[FilterProfile] | None = None,
    ) -> list[ScoredHackathon]:
        profiles = profiles if profiles is not None else self.active_profiles()
        if not profiles:
            # No filters configured → everything passes with neutral score
            return [ScoredHackathon(hackathon=item, score=0.0, matched_rules=[]) for item in hackathons]

        scored: dict[str, ScoredHackathon] = {}
        for profile in profiles:
            for hackathon in hackathons:
                total = 0.0
                matched: list[str] = []
                rejected = False
                for rule in self.rules:
                    delta, hard_fail = rule.score(hackathon, profile)
                    if hard_fail:
                        rejected = True
                        break
                    if delta:
                        total += delta
                        matched.append(rule.name)
                if rejected:
                    continue
                key = hackathon.dedupe_key
                current = scored.get(key)
                if current is None or total > current.score:
                    scored[key] = ScoredHackathon(
                        hackathon=hackathon,
                        score=total,
                        matched_rules=matched,
                    )
        return sorted(scored.values(), key=lambda item: item.score, reverse=True)
