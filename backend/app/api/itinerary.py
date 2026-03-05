from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.attraction import Attraction
from app.models.itinerary import ItineraryActivity, ItineraryDay
from app.models.trip import Trip
from app.models.user import User
from app.schemas.itinerary import ItineraryDayRead, ItineraryDayUpdate, ItineraryOverview, ItinerarySwapRequest
from app.services.itinerary_generator import generate_itinerary

log = structlog.get_logger()
router = APIRouter(prefix="/trips/{trip_id}/itinerary", tags=["itinerary"])


@router.get("", response_model=ItineraryOverview)
async def get_itinerary(
    trip_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await _get_user_trip(trip_id, user.id, db)

    result = await db.execute(
        select(ItineraryDay)
        .options(selectinload(ItineraryDay.activities))
        .where(ItineraryDay.trip_id == trip_id)
        .order_by(ItineraryDay.day_number)
    )
    days = result.scalars().all()

    total_activities = sum(len(d.activities) for d in days)
    booked = sum(
        1 for d in days for a in d.activities if a.booking_status == "booked"
    )
    needs_booking = sum(
        1 for d in days for a in d.activities if a.booking_status == "needs-booking"
    )
    flex_days = sum(1 for d in days if d.is_flex_day)

    return ItineraryOverview(
        trip_id=trip_id,
        total_days=len(days),
        total_activities=total_activities,
        booked_count=booked,
        needs_booking_count=needs_booking,
        flex_days=flex_days,
        days=[ItineraryDayRead.model_validate(d) for d in days],
    )


@router.post("/generate", response_model=ItineraryOverview, status_code=status.HTTP_201_CREATED)
async def generate_trip_itinerary(
    trip_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await _get_user_trip(trip_id, user.id, db)

    existing = await db.execute(
        select(ItineraryDay).where(ItineraryDay.trip_id == trip_id).limit(1)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Itinerary already exists. Delete it first to regenerate.",
        )

    result = await db.execute(select(Attraction).where(Attraction.destination == "new-zealand"))
    all_attractions = result.scalars().all()

    planning_state = trip.planning_state or {}
    attraction_dicts = [
        {
            "name": a.name,
            "slug": a.slug,
            "types": a.types,
            "location_name": a.location_name,
            "region": a.region,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "difficulty": a.difficulty,
            "cost_level": a.cost_level,
            "duration_min": a.duration_min,
            "duration_max": a.duration_max,
            "booking_required": a.booking_required,
            "uniqueness_score": a.uniqueness_score,
            "logistics": a.logistics,
            "pro_tips": a.pro_tips,
        }
        for a in all_attractions
    ]

    itinerary_data = await generate_itinerary(planning_state, attraction_dicts)

    days = []
    for day_data in itinerary_data:
        day = ItineraryDay(
            trip_id=trip_id,
            day_number=day_data["day_number"],
            location=day_data["location"],
            title=day_data.get("title"),
            is_flex_day=day_data.get("is_flex_day", False),
            is_arrival=day_data.get("is_arrival", False),
            is_departure=day_data.get("is_departure", False),
            accommodation=day_data.get("accommodation", {}),
            transport=day_data.get("transport", {}),
        )
        db.add(day)
        await db.flush()

        for act_data in day_data.get("activities", []):
            activity = ItineraryActivity(
                itinerary_day_id=day.id,
                name=act_data["name"],
                emoji=act_data.get("emoji", "📍"),
                provider=act_data.get("provider"),
                time_start=act_data.get("time_start"),
                time_end=act_data.get("time_end"),
                price=act_data.get("price", 0),
                currency=act_data.get("currency", "NZD"),
                booking_status=act_data.get("booking_status", "not-booked"),
                sort_order=act_data.get("sort_order", 0),
            )
            db.add(activity)

        days.append(day)

    await db.flush()

    for day in days:
        await db.refresh(day)

    result2 = await db.execute(
        select(ItineraryDay)
        .options(selectinload(ItineraryDay.activities))
        .where(ItineraryDay.trip_id == trip_id)
        .order_by(ItineraryDay.day_number)
    )
    refreshed_days = result2.scalars().all()

    total_activities = sum(len(d.activities) for d in refreshed_days)

    log.info("itinerary_generated", trip_id=str(trip_id), days=len(refreshed_days), activities=total_activities)

    return ItineraryOverview(
        trip_id=trip_id,
        total_days=len(refreshed_days),
        total_activities=total_activities,
        booked_count=0,
        needs_booking_count=0,
        flex_days=sum(1 for d in refreshed_days if d.is_flex_day),
        days=[ItineraryDayRead.model_validate(d) for d in refreshed_days],
    )


@router.get("/days", response_model=list[ItineraryDayRead])
async def list_days(
    trip_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_trip(trip_id, user.id, db)

    result = await db.execute(
        select(ItineraryDay)
        .options(selectinload(ItineraryDay.activities))
        .where(ItineraryDay.trip_id == trip_id)
        .order_by(ItineraryDay.day_number)
    )
    days = result.scalars().all()
    return [ItineraryDayRead.model_validate(d) for d in days]


@router.get("/days/{day_number}", response_model=ItineraryDayRead)
async def get_day(
    trip_id: uuid.UUID,
    day_number: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_trip(trip_id, user.id, db)

    result = await db.execute(
        select(ItineraryDay)
        .options(selectinload(ItineraryDay.activities))
        .where(ItineraryDay.trip_id == trip_id, ItineraryDay.day_number == day_number)
    )
    day = result.scalar_one_or_none()
    if day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")
    return day


@router.patch("/days/{day_number}", response_model=ItineraryDayRead)
async def update_day(
    trip_id: uuid.UUID,
    day_number: int,
    body: ItineraryDayUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_trip(trip_id, user.id, db)

    result = await db.execute(
        select(ItineraryDay)
        .options(selectinload(ItineraryDay.activities))
        .where(ItineraryDay.trip_id == trip_id, ItineraryDay.day_number == day_number)
    )
    day = result.scalar_one_or_none()
    if day is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(day, field, value)

    await db.flush()
    await db.refresh(day)
    return day


@router.post("/swap")
async def apply_itinerary_swap(
    trip_id: uuid.UUID,
    body: ItinerarySwapRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_trip(trip_id, user.id, db)

    result_a = await db.execute(
        select(ItineraryDay)
        .options(selectinload(ItineraryDay.activities))
        .where(ItineraryDay.trip_id == trip_id, ItineraryDay.day_number == body.day_a)
    )
    day_a = result_a.scalar_one_or_none()

    result_b = await db.execute(
        select(ItineraryDay)
        .options(selectinload(ItineraryDay.activities))
        .where(ItineraryDay.trip_id == trip_id, ItineraryDay.day_number == body.day_b)
    )
    day_b = result_b.scalar_one_or_none()

    if not day_a or not day_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both days not found")

    if day_a.is_locked or day_b.is_locked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot swap locked days")

    day_a.day_number, day_b.day_number = day_b.day_number, day_a.day_number
    if day_a.date and day_b.date:
        day_a.date, day_b.date = day_b.date, day_a.date

    await db.flush()
    log.info("itinerary_days_swapped", trip_id=str(trip_id), day_a=body.day_a, day_b=body.day_b)

    return {"status": "swapped", "message": f"Days {body.day_a} and {body.day_b} have been swapped."}


async def _get_user_trip(trip_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Trip:
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id)
    )
    trip = result.scalar_one_or_none()
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip
