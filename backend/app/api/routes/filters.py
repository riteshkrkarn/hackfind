from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.schemas import FilterProfileIn, FilterProfileOut
from app.db.models import FilterProfile
from app.db.session import get_session

router = APIRouter(prefix="/filters", tags=["filters"])


def to_out(profile: FilterProfile) -> FilterProfileOut:
    return FilterProfileOut(
        id=profile.id,
        name=profile.name,
        active=profile.active,
        tech_stack=profile.tech_stack or [],
        modes=profile.modes or [],
        domains=profile.domains or [],
        min_prize=profile.min_prize,
        max_prize=profile.max_prize,
        team_size_min=profile.team_size_min,
        team_size_max=profile.team_size_max,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get("", response_model=list[FilterProfileOut])
def list_filters(session: Session = Depends(get_session)) -> list[FilterProfileOut]:
    rows = session.exec(select(FilterProfile).order_by(FilterProfile.id)).all()
    return [to_out(row) for row in rows]


@router.post("", response_model=FilterProfileOut, status_code=201)
def create_filter(
    body: FilterProfileIn,
    session: Session = Depends(get_session),
) -> FilterProfileOut:
    profile = FilterProfile(**body.model_dump())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return to_out(profile)


@router.put("/{filter_id}", response_model=FilterProfileOut)
def update_filter(
    filter_id: int,
    body: FilterProfileIn,
    session: Session = Depends(get_session),
) -> FilterProfileOut:
    profile = session.get(FilterProfile, filter_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Filter profile not found")
    for key, value in body.model_dump().items():
        setattr(profile, key, value)
    profile.updated_at = datetime.utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return to_out(profile)


@router.delete("/{filter_id}", status_code=204)
def delete_filter(filter_id: int, session: Session = Depends(get_session)) -> None:
    profile = session.get(FilterProfile, filter_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Filter profile not found")
    session.delete(profile)
    session.commit()
