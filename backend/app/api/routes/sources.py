from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.db.models import CustomSource
from app.db.session import get_session
from app.sources.definition import SourceKind

router = APIRouter(prefix="/sources", tags=["sources"])


class CustomSourceIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    kind: SourceKind
    enabled: bool = True
    config: dict = Field(default_factory=dict)


class CustomSourceOut(CustomSourceIn):
    id: int
    created_at: datetime
    updated_at: datetime


def to_out(row: CustomSource) -> CustomSourceOut:
    return CustomSourceOut(
        id=row.id,
        name=row.name,
        kind=row.kind,  # type: ignore[arg-type]
        enabled=row.enabled,
        config=row.config or {},
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("", response_model=list[CustomSourceOut])
def list_sources(session: Session = Depends(get_session)) -> list[CustomSourceOut]:
    rows = session.exec(select(CustomSource).order_by(CustomSource.id)).all()
    return [to_out(row) for row in rows]


@router.post("", response_model=CustomSourceOut, status_code=201)
def create_source(
    body: CustomSourceIn,
    session: Session = Depends(get_session),
) -> CustomSourceOut:
    existing = session.exec(
        select(CustomSource).where(CustomSource.name == body.name)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Source name already exists")
    row = CustomSource(**body.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return to_out(row)


@router.put("/{source_id}", response_model=CustomSourceOut)
def update_source(
    source_id: int,
    body: CustomSourceIn,
    session: Session = Depends(get_session),
) -> CustomSourceOut:
    row = session.get(CustomSource, source_id)
    if not row:
        raise HTTPException(status_code=404, detail="Source not found")
    clash = session.exec(
        select(CustomSource).where(
            CustomSource.name == body.name,
            CustomSource.id != source_id,
        )
    ).first()
    if clash:
        raise HTTPException(status_code=409, detail="Source name already exists")
    for key, value in body.model_dump().items():
        setattr(row, key, value)
    row.updated_at = datetime.utcnow()
    session.add(row)
    session.commit()
    session.refresh(row)
    return to_out(row)


@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: int, session: Session = Depends(get_session)) -> None:
    row = session.get(CustomSource, source_id)
    if not row:
        raise HTTPException(status_code=404, detail="Source not found")
    session.delete(row)
    session.commit()
