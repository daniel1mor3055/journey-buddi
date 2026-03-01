from __future__ import annotations

from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.attraction import Attraction
from app.schemas.attraction import AttractionRead, AttractionSummary

log = structlog.get_logger()
router = APIRouter(prefix="/attractions", tags=["attractions"])


@router.get("", response_model=list)
async def list_attractions(
    destination: str = "new-zealand",
    region: Optional[str] = None,
    types: Optional[str] = Query(None, description="Comma-separated activity types"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Attraction).where(Attraction.destination == destination)
    if region:
        query = query.where(Attraction.region == region)
    if types:
        type_list = [t.strip() for t in types.split(",")]
        query = query.where(Attraction.types.overlap(type_list))
    query = query.order_by(Attraction.uniqueness_score.desc())

    result = await db.execute(query)
    attractions = result.scalars().all()
    return [AttractionSummary.model_validate(a) for a in attractions]


@router.get("/{slug}", response_model=AttractionRead)
async def get_attraction(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Attraction).where(Attraction.slug == slug)
    )
    attraction = result.scalar_one_or_none()
    if attraction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attraction not found")
    return attraction


@router.get("/{slug}/tips")
async def get_attraction_tips(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Attraction).where(Attraction.slug == slug)
    )
    attraction = result.scalar_one_or_none()
    if attraction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attraction not found")
    return {"slug": slug, "name": attraction.name, "pro_tips": attraction.pro_tips or []}


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_attractions(
    db: AsyncSession = Depends(get_db),
):
    """Seed the database with NZ attractions. Idempotent — skips existing slugs."""
    from app.data.nz_attractions import NZ_ATTRACTIONS

    count = await db.execute(select(sa_func.count()).select_from(Attraction))
    existing = count.scalar()
    if existing and existing > 0:
        return {"message": f"Database already has {existing} attractions, skipping seed"}

    created = 0
    for data in NZ_ATTRACTIONS:
        attraction = Attraction(
            destination=data["destination"],
            region=data.get("region"),
            name=data["name"],
            slug=data["slug"],
            description=data.get("description"),
            types=data.get("types", []),
            location_name=data.get("location_name"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            difficulty=data.get("difficulty"),
            cost_level=data.get("cost_level"),
            duration_min=data.get("duration_min"),
            duration_max=data.get("duration_max"),
            seasonal_availability=data.get("seasonal_availability", "year-round"),
            booking_required=data.get("booking_required", False),
            weather_sensitivity=data.get("weather_sensitivity", "moderate"),
            ideal_conditions=data.get("ideal_conditions", {}),
            acceptable_conditions=data.get("acceptable_conditions", {}),
            dealbreaker_conditions=data.get("dealbreaker_conditions", {}),
            logistics=data.get("logistics", {}),
            pro_tips=data.get("pro_tips", []),
            uniqueness_score=data.get("uniqueness_score", 50),
            metadata_=data.get("metadata", {}),
        )
        db.add(attraction)
        created += 1

    await db.flush()
    log.info("attractions_seeded", count=created)
    return {"message": f"Seeded {created} attractions"}
