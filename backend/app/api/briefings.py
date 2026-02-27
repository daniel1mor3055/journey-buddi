from __future__ import annotations

from datetime import date, datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.briefing import DailyBriefing, SwapSuggestion
from app.models.itinerary import ItineraryDay, ItineraryActivity
from app.models.trip import Trip
from app.models.user import User
from app.schemas.briefing import (
    DailyBriefingRead,
    SwapSuggestionRead,
    BriefingGenerateRequest,
    SwapActionRequest,
)
from app.services.briefing_generator import generate_briefing_for_day
from app.services.swap_engine import detect_swap_opportunities, accept_swap, decline_swap

log = structlog.get_logger()
router = APIRouter(prefix="/trips/{trip_id}/briefings", tags=["briefings"])


@router.get("")
async def list_briefings(
    trip_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DailyBriefingRead]:
    trip = await _get_trip(db, trip_id, user.id)

    result = await db.execute(
        select(DailyBriefing)
        .where(DailyBriefing.trip_id == trip.id)
        .order_by(DailyBriefing.day_number)
    )
    briefings = result.scalars().all()
    return [DailyBriefingRead.model_validate(b) for b in briefings]


@router.get("/{day_number}")
async def get_briefing(
    trip_id: str,
    day_number: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DailyBriefingRead:
    trip = await _get_trip(db, trip_id, user.id)

    result = await db.execute(
        select(DailyBriefing)
        .where(DailyBriefing.trip_id == trip.id, DailyBriefing.day_number == day_number)
        .order_by(DailyBriefing.created_at.desc())
        .limit(1)
    )
    briefing = result.scalar_one_or_none()

    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found for this day")

    return DailyBriefingRead.model_validate(briefing)


@router.post("/generate")
async def generate_briefings(
    trip_id: str,
    request: BriefingGenerateRequest = BriefingGenerateRequest(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DailyBriefingRead]:
    trip = await _get_trip(db, trip_id, user.id)

    days_query = (
        select(ItineraryDay)
        .where(ItineraryDay.trip_id == trip.id)
        .options(
            selectinload(ItineraryDay.activities).selectinload(ItineraryActivity.attraction)
        )
        .order_by(ItineraryDay.day_number)
    )

    if request.day_number is not None:
        days_query = days_query.where(ItineraryDay.day_number == request.day_number)

    result = await db.execute(days_query)
    days = result.scalars().all()

    if not days:
        raise HTTPException(status_code=404, detail="No itinerary days found")

    generated = []
    for day in days:
        if not request.force_refresh:
            existing = await db.execute(
                select(DailyBriefing)
                .where(
                    DailyBriefing.trip_id == trip.id,
                    DailyBriefing.day_number == day.day_number,
                )
                .order_by(DailyBriefing.created_at.desc())
                .limit(1)
            )
            existing_briefing = existing.scalar_one_or_none()
            if existing_briefing:
                age = (datetime.now(timezone.utc) - existing_briefing.created_at.replace(tzinfo=timezone.utc)).total_seconds()
                if age < 3600:
                    generated.append(DailyBriefingRead.model_validate(existing_briefing))
                    continue

        briefing = await generate_briefing_for_day(db, trip, day)
        generated.append(DailyBriefingRead.model_validate(briefing))

    swap_suggestions = await detect_swap_opportunities(db, trip, list(days))
    if swap_suggestions:
        log.info("swap_opportunities_detected", trip_id=str(trip.id), count=len(swap_suggestions))

    return generated


@router.get("/swaps/list")
async def list_swaps(
    trip_id: str,
    status: str = Query(default="pending"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SwapSuggestionRead]:
    trip = await _get_trip(db, trip_id, user.id)

    result = await db.execute(
        select(SwapSuggestion)
        .where(SwapSuggestion.trip_id == trip.id, SwapSuggestion.status == status)
        .order_by(SwapSuggestion.created_at.desc())
    )
    swaps = result.scalars().all()
    return [SwapSuggestionRead.model_validate(s) for s in swaps]


@router.post("/swaps/{swap_id}/action")
async def swap_action(
    trip_id: str,
    swap_id: str,
    request: SwapActionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await _get_trip(db, trip_id, user.id)

    result = await db.execute(
        select(SwapSuggestion)
        .where(SwapSuggestion.id == swap_id, SwapSuggestion.trip_id == trip.id)
    )
    swap = result.scalar_one_or_none()
    if not swap:
        raise HTTPException(status_code=404, detail="Swap suggestion not found")

    if swap.status != "pending":
        raise HTTPException(status_code=400, detail=f"Swap is already {swap.status}")

    if request.action == "accept":
        success = await accept_swap(db, swap)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to apply swap")
        return {"status": "accepted", "message": "Itinerary updated with the swap."}

    elif request.action == "decline":
        await decline_swap(db, swap)
        return {"status": "declined", "message": "Swap declined. We'll make the best of the current plan."}

    else:
        raise HTTPException(status_code=400, detail="Action must be 'accept' or 'decline'")


async def _get_trip(db: AsyncSession, trip_id: str, user_id) -> Trip:
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
