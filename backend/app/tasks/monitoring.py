from __future__ import annotations

import asyncio
from datetime import date, timedelta

import structlog

from app.celery_app import celery_app

log = structlog.get_logger()


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _refresh_active_trip_conditions():
    from app.database import async_session_factory
    from app.models.trip import Trip
    from app.models.itinerary import ItineraryDay, ItineraryActivity
    from app.services.weather import weather_service
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with async_session_factory() as db:
        result = await db.execute(
            select(Trip).where(Trip.status == "active")
        )
        active_trips = result.scalars().all()

        for trip in active_trips:
            days_result = await db.execute(
                select(ItineraryDay)
                .where(ItineraryDay.trip_id == trip.id)
                .options(
                    selectinload(ItineraryDay.activities)
                    .selectinload(ItineraryActivity.attraction)
                )
                .order_by(ItineraryDay.day_number)
                .limit(5)
            )
            days = days_result.scalars().all()

            for day in days:
                for act in day.activities:
                    if act.attraction and act.attraction.latitude and act.attraction.longitude:
                        await weather_service.get_hourly_forecast(
                            act.attraction.latitude,
                            act.attraction.longitude,
                            days=5,
                        )
                        break

            log.info("conditions_refreshed", trip_id=str(trip.id), days=len(days))


@celery_app.task(name="app.tasks.monitoring.refresh_conditions")
def refresh_conditions():
    log.info("task_refresh_conditions_start")
    _run_async(_refresh_active_trip_conditions())
    log.info("task_refresh_conditions_done")


async def _check_condition_alerts():
    from app.database import async_session_factory
    from app.models.trip import Trip
    from app.models.itinerary import ItineraryDay, ItineraryActivity
    from app.models.briefing import DailyBriefing
    from app.services.weather import weather_service
    from app.services.condition_scorer import score_day_conditions
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from datetime import datetime, timezone

    async with async_session_factory() as db:
        result = await db.execute(
            select(Trip).where(Trip.status == "active")
        )
        active_trips = result.scalars().all()

        for trip in active_trips:
            if not trip.start_date:
                continue

            today = date.today()
            day_number = (today - trip.start_date).days + 1

            days_result = await db.execute(
                select(ItineraryDay)
                .where(
                    ItineraryDay.trip_id == trip.id,
                    ItineraryDay.day_number == day_number,
                )
                .options(
                    selectinload(ItineraryDay.activities)
                    .selectinload(ItineraryActivity.attraction)
                )
            )
            day = days_result.scalar_one_or_none()
            if not day:
                continue

            briefing_result = await db.execute(
                select(DailyBriefing)
                .where(
                    DailyBriefing.trip_id == trip.id,
                    DailyBriefing.day_number == day_number,
                )
                .order_by(DailyBriefing.created_at.desc())
                .limit(1)
            )
            briefing = briefing_result.scalar_one_or_none()

            if not briefing:
                continue

            previous_assessment = briefing.overall_assessment

            lat, lon = None, None
            activities = []
            for act in day.activities:
                if act.attraction and act.attraction.latitude and act.attraction.longitude:
                    if lat is None:
                        lat, lon = act.attraction.latitude, act.attraction.longitude
                    activities.append({
                        "id": str(act.id),
                        "name": act.name,
                        "types": act.attraction.types if act.attraction.types else ["hiking"],
                        "time_start": act.time_start,
                    })

            if lat is None:
                continue

            hourly = await weather_service.get_hourly_forecast(lat, lon, days=1)
            day_hourly = [w for w in hourly if w.timestamp.date() == today]

            if not day_hourly:
                continue

            report = score_day_conditions(
                day_hourly, activities, day_number, today.isoformat(), day.location, "high"
            )

            severity_order = ["EXCELLENT", "GOOD", "FAIR", "POOR", "UNSAFE"]
            prev_idx = severity_order.index(previous_assessment) if previous_assessment in severity_order else 1
            new_idx = severity_order.index(report.overall_assessment) if report.overall_assessment in severity_order else 1

            if new_idx - prev_idx >= 2:
                log.warning(
                    "condition_alert_triggered",
                    trip_id=str(trip.id),
                    day=day_number,
                    previous=previous_assessment,
                    current=report.overall_assessment,
                    score=report.overall_score,
                )


@celery_app.task(name="app.tasks.monitoring.check_alerts")
def check_alerts():
    log.info("task_check_alerts_start")
    _run_async(_check_condition_alerts())
    log.info("task_check_alerts_done")
