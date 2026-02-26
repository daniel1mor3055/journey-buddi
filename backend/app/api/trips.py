import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripRead, TripUpdate

router = APIRouter(prefix="/trips", tags=["trips"])

VALID_STATUSES = {"planning", "confirmed", "active", "completed", "archived"}


@router.post("", response_model=TripRead, status_code=status.HTTP_201_CREATED)
async def create_trip(
    body: TripCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = Trip(user_id=user.id, **body.model_dump())
    db.add(trip)
    await db.flush()
    await db.refresh(trip)
    return trip


@router.get("", response_model=list[TripRead])
async def list_trips(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trip).where(Trip.user_id == user.id).order_by(Trip.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{trip_id}", response_model=TripRead)
async def get_trip(
    trip_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await _get_user_trip(trip_id, user.id, db)
    return trip


@router.patch("/{trip_id}", response_model=TripRead)
async def update_trip(
    trip_id: uuid.UUID,
    body: TripUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await _get_user_trip(trip_id, user.id, db)
    update_data = body.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}",
        )

    for field, value in update_data.items():
        setattr(trip, field, value)

    await db.flush()
    await db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    trip = await _get_user_trip(trip_id, user.id, db)
    await db.delete(trip)


async def _get_user_trip(
    trip_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession
) -> Trip:
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id)
    )
    trip = result.scalar_one_or_none()
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip
