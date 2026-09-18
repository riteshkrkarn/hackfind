from sqlmodel import Session, select

from app.db.models import SeenHash
from app.schemas.hackathon import Hackathon


class DeduplicationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def filter_new(self, hackathons: list[Hackathon]) -> list[Hackathon]:
        if not hackathons:
            return []

        keys = [item.dedupe_key for item in hackathons]
        existing = set(
            self.session.exec(select(SeenHash.dedupe_key).where(SeenHash.dedupe_key.in_(keys))).all()
        )
        return [item for item in hackathons if item.dedupe_key not in existing]

    def mark_seen(self, hackathons: list[Hackathon]) -> None:
        for item in hackathons:
            if self.session.get(SeenHash, item.dedupe_key):
                continue
            self.session.add(SeenHash(dedupe_key=item.dedupe_key))
        self.session.commit()
