from datetime import date, timedelta

from app.schemas.hackathon import Hackathon, HackathonMode
from app.sources.base import SourceAdapter


class SeedSource(SourceAdapter):
    """Deterministic sample events so the agent pipeline works offline."""

    name = "seed"

    def fetch(self) -> list[Hackathon]:
        today = date.today()
        return [
            Hackathon(
                external_id="seed-campus-ai",
                source=self.name,
                title="Campus AI Sprint",
                url="https://example.com/hackathons/campus-ai-sprint",
                description="48-hour AI build for student teams.",
                mode=HackathonMode.in_person,
                location="Bengaluru",
                starts_on=today + timedelta(days=20),
                ends_on=today + timedelta(days=22),
                apply_by=today + timedelta(days=6),
                prize_amount=5000,
                team_size_min=1,
                team_size_max=4,
                tech_stack=["python", "llm", "react"],
                domains=["ai"],
            ),
            Hackathon(
                external_id="seed-healthtech",
                source=self.name,
                title="HealthTech Build Weekend",
                url="https://example.com/hackathons/healthtech-weekend",
                description="Remote healthtech prototypes with mentors.",
                mode=HackathonMode.remote,
                starts_on=today + timedelta(days=30),
                ends_on=today + timedelta(days=32),
                apply_by=today + timedelta(days=12),
                prize_amount=10000,
                team_size_min=2,
                team_size_max=5,
                tech_stack=["typescript", "fhir", "react"],
                domains=["healthtech"],
            ),
            Hackathon(
                external_id="seed-fintech",
                source=self.name,
                title="Fintech Fellows Hack",
                url="https://example.com/hackathons/fintech-fellows",
                description="Hybrid fintech challenge focused on payments.",
                mode=HackathonMode.hybrid,
                location="Hyderabad",
                starts_on=today + timedelta(days=14),
                ends_on=today + timedelta(days=15),
                apply_by=today + timedelta(days=2),
                prize_amount=8000,
                team_size_min=1,
                team_size_max=4,
                tech_stack=["kotlin", "nodejs"],
                domains=["fintech"],
            ),
        ]
