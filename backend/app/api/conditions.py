from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.itinerary import ItineraryDay, ItineraryActivity
from app.models.trip import Trip
from app.models.user import User
from app.schemas.conditions import (
    CurrentConditionsResponse,
    DayConditionReport,
    ConditionForecastResponse,
    WeatherCondition,
)
from app.services.weather import weather_service
from app.services.solar import solar_service
from app.services.condition_scorer import score_day_conditions

log = structlog.get_logger()
router = APIRouter(prefix="/conditions", tags=["conditions"])


@router.get("/current")
async def get_current_conditions(
    lat: float = Query(...),
    lon: float = Query(...),
    user: User = Depends(get_current_user),
) -> CurrentConditionsResponse:
    weather = await weather_service.get_conditions_for_datetime(lat, lon, datetime.now(timezone.utc))
    solar = await solar_service.get_solar(lat, lon, date.today())

    return CurrentConditionsResponse(
        lat=lat,
        lon=lon,
        weather=weather,
        solar=solar,
        fetched_at=datetime.now(timezone.utc),
    )


@router.get("/forecast/{trip_id}")
async def get_trip_condition_forecast(
    trip_id: str,
    days_ahead: int = Query(default=5, ge=1, le=8),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConditionForecastResponse:
    result = await db.execute(
        select(Trip)
        .where(Trip.id == trip_id, Trip.user_id == user.id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    days_result = await db.execute(
        select(ItineraryDay)
        .where(ItineraryDay.trip_id == trip.id)
        .options(
            selectinload(ItineraryDay.activities).selectinload(ItineraryActivity.attraction)
        )
        .order_by(ItineraryDay.day_number)
    )
    itinerary_days = days_result.scalars().all()

    if not itinerary_days:
        raise HTTPException(status_code=404, detail="No itinerary found for this trip")

    today = date.today()
    day_reports = []

    for day in itinerary_days[:days_ahead]:
        day_date = day.date or (trip.start_date + timedelta(days=day.day_number - 1) if trip.start_date else today + timedelta(days=day.day_number - 1))

        lat, lon = _get_day_coords(day)
        hourly = await weather_service.get_hourly_forecast(lat, lon, days=8)
        day_hourly = [w for w in hourly if w.timestamp.date() == day_date]

        if not day_hourly and hourly:
            day_hourly = hourly[:24]

        activities = []
        for act in day.activities:
            act_types = act.attraction.types if act.attraction and act.attraction.types else ["hiking"]
            activities.append({
                "id": str(act.id),
                "name": act.name,
                "types": act_types,
                "time_start": act.time_start,
            })

        hours_ahead = max(0, (datetime.combine(day_date, datetime.min.time()) - datetime.combine(today, datetime.min.time())).total_seconds() / 3600)
        if hours_ahead <= 48:
            confidence = "high"
        elif hours_ahead <= 120:
            confidence = "medium"
        else:
            confidence = "low"

        report = score_day_conditions(
            day_hourly,
            activities,
            day.day_number,
            day_date.isoformat() if day_date else None,
            day.location,
            confidence,
        )
        day_reports.append(report)

    return ConditionForecastResponse(
        trip_id=str(trip.id),
        generated_at=datetime.now(timezone.utc),
        days=day_reports,
    )


@router.post("/trips/{trip_id}/activate")
async def activate_trip(
    trip_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Trip).where(Trip.id == trip_id, Trip.user_id == user.id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip.status not in ("confirmed", "planning"):
        raise HTTPException(status_code=400, detail=f"Trip cannot be activated from status '{trip.status}'")

    trip.status = "active"
    log.info("trip_activated", trip_id=str(trip.id))

    return {"status": "active", "trip_id": str(trip.id), "message": "Trip activated. Live companion mode enabled."}


def _get_day_coords(day: ItineraryDay) -> tuple[float, float]:
    if day.activities:
        for act in day.activities:
            if act.attraction and act.attraction.latitude and act.attraction.longitude:
                return (act.attraction.latitude, act.attraction.longitude)

    from app.services.briefing_generator import _get_day_coordinates
    return _get_day_coordinates(day)
