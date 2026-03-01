from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.briefing import SwapSuggestion
from app.models.trip import Trip
from app.models.user import User
from app.schemas.briefing import SwapSuggestionRead
from app.services.swap_engine import accept_swap, decline_swap

log = structlog.get_logger()
router = APIRouter(prefix="/trips/{trip_id}/swaps", tags=["swaps"])


@router.get("")
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


@router.get("/{swap_id}")
async def get_swap(
    trip_id: str,
    swap_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SwapSuggestionRead:
    trip = await _get_trip(db, trip_id, user.id)

    result = await db.execute(
        select(SwapSuggestion)
        .where(SwapSuggestion.id == swap_id, SwapSuggestion.trip_id == trip.id)
    )
    swap = result.scalar_one_or_none()
    if not swap:
        raise HTTPException(status_code=404, detail="Swap suggestion not found")

    return SwapSuggestionRead.model_validate(swap)


@router.post("/{swap_id}/accept")
async def accept_swap_suggestion(
    trip_id: str,
    swap_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    swap = await _get_pending_swap(db, trip_id, swap_id, user.id)

    success = await accept_swap(db, swap)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to apply swap")

    return {"status": "accepted", "message": "Itinerary updated with the swap."}


@router.post("/{swap_id}/decline")
async def decline_swap_suggestion(
    trip_id: str,
    swap_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    swap = await _get_pending_swap(db, trip_id, swap_id, user.id)

    await decline_swap(db, swap)

    return {"status": "declined", "message": "Swap declined. We'll make the best of the current plan."}


async def _get_pending_swap(
    db: AsyncSession, trip_id: str, swap_id: str, user_id
) -> SwapSuggestion:
    trip = await _get_trip(db, trip_id, user_id)

    result = await db.execute(
        select(SwapSuggestion)
        .where(SwapSuggestion.id == swap_id, SwapSuggestion.trip_id == trip.id)
    )
    swap = result.scalar_one_or_none()
    if not swap:
        raise HTTPException(status_code=404, detail="Swap suggestion not found")

    if swap.status != "pending":
        raise HTTPException(status_code=400, detail=f"Swap is already {swap.status}")

    return swap


async def _get_trip(db: AsyncSession, trip_id: str, user_id) -> Trip:
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
