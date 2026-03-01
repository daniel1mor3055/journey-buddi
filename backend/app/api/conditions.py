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
    ActivityConditionReport,
    CurrentConditionsResponse,
    DayConditionReport,
    ConditionForecastResponse,
    WeatherCondition,
)
from app.services.weather import weather_service
from app.services.solar import solar_service
from app.services.condition_scorer import score_activity_conditions, score_day_conditions

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



@router.get("/assess")
async def assess_activity_conditions(
    activity_id: str = Query(...),
    date_str: str = Query(..., alias="date"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ActivityConditionReport:
    result = await db.execute(
        select(ItineraryActivity)
        .options(selectinload(ItineraryActivity.attraction))
        .where(ItineraryActivity.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    act_types = (
        activity.attraction.types
        if activity.attraction and activity.attraction.types
        else ["hiking"]
    )

    if activity.attraction and activity.attraction.latitude and activity.attraction.longitude:
        lat, lon = activity.attraction.latitude, activity.attraction.longitude
    else:
        lat, lon = -41.2865, 174.7762  # Wellington fallback

    target_date = date.fromisoformat(date_str)
    hours_ahead = max(
        0,
        (
            datetime.combine(target_date, datetime.min.time())
            - datetime.combine(date.today(), datetime.min.time())
        ).total_seconds()
        / 3600,
    )
    if hours_ahead <= 48:
        confidence = "high"
    elif hours_ahead <= 120:
        confidence = "medium"
    else:
        confidence = "low"

    hourly = await weather_service.get_hourly_forecast(lat, lon, days=8)
    day_hourly = [w for w in hourly if w.timestamp.date() == target_date]

    if not day_hourly and hourly:
        day_hourly = hourly[:24]

    if not day_hourly:
        raise HTTPException(status_code=404, detail="No weather data available for this date")

    target_hour = int(activity.time_start.split(":")[0]) if activity.time_start and ":" in activity.time_start else 12
    weather = min(day_hourly, key=lambda w: abs(w.timestamp.hour - target_hour))

    report = score_activity_conditions(weather, activity.name, act_types, confidence)
    report.activity_id = str(activity.id)
    return report


def _get_day_coords(day: ItineraryDay) -> tuple[float, float]:
    if day.activities:
        for act in day.activities:
            if act.attraction and act.attraction.latitude and act.attraction.longitude:
                return (act.attraction.latitude, act.attraction.longitude)

    from app.services.briefing_generator import _get_day_coordinates
    return _get_day_coordinates(day)
