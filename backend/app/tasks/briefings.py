from __future__ import annotations

import asyncio
from datetime import date, datetime, timezone

import structlog

from app.celery_app import celery_app

log = structlog.get_logger()


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _check_and_generate_briefings():
    from app.database import async_session_factory
    from app.models.trip import Trip
    from app.models.briefing import DailyBriefing
    from app.models.itinerary import ItineraryDay, ItineraryActivity
    from app.services.briefing_generator import generate_briefing_for_day
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with async_session_factory() as db:
        result = await db.execute(
            select(Trip).where(Trip.status == "active")
        )
        active_trips = result.scalars().all()

        today = date.today()
        now = datetime.now(timezone.utc)

        for trip in active_trips:
            if not trip.start_date:
                continue

            day_number = (today - trip.start_date).days + 1

            existing = await db.execute(
                select(DailyBriefing)
                .where(
                    DailyBriefing.trip_id == trip.id,
                    DailyBriefing.day_number == day_number,
                )
                .order_by(DailyBriefing.created_at.desc())
                .limit(1)
            )
            briefing = existing.scalar_one_or_none()

            if briefing:
                age = (now - briefing.created_at.replace(tzinfo=timezone.utc)).total_seconds()
                if age < 3600:
                    continue

            day_result = await db.execute(
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
            day = day_result.scalar_one_or_none()

            if not day:
                continue

            await generate_briefing_for_day(db, trip, day)
            await db.commit()
            log.info("briefing_auto_generated", trip_id=str(trip.id), day=day_number)


@celery_app.task(name="app.tasks.briefings.check_and_generate")
def check_and_generate():
    log.info("task_check_and_generate_start")
    _run_async(_check_and_generate_briefings())
    log.info("task_check_and_generate_done")
