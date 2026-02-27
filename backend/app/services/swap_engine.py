from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Optional

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.briefing import SwapSuggestion
from app.models.itinerary import ItineraryDay, ItineraryActivity
from app.models.trip import Trip
from app.services.weather import weather_service
from app.services.condition_scorer import score_activity_conditions, score_to_assessment
from app.services.gemini import gemini_client

log = structlog.get_logger()

SWAP_SYSTEM_PROMPT = """You are Buddi, the travel companion. A swap has been detected where conditions are better on a different day.

Generate a JSON response explaining the swap:
{
  "headline": "Short 1-line summary of the suggestion",
  "reasoning": "2-3 sentences explaining why the swap is better",
  "what_changes": "What the user needs to do (bookings, logistics)",
  "what_stays_same": "Reassurance about what doesn't change",
  "tips_if_declined": "1-2 tips for making the best of suboptimal conditions if user keeps original plan"
}

Be specific with weather numbers. Be honest and helpful."""


async def detect_swap_opportunities(
    db: AsyncSession,
    trip: Trip,
    days: list[ItineraryDay],
) -> list[SwapSuggestion]:
    if not days or len(days) < 2:
        return []

    existing = await db.execute(
        select(SwapSuggestion)
        .where(SwapSuggestion.trip_id == trip.id)
        .where(SwapSuggestion.status.in_(["pending", "declined"]))
    )
    existing_swaps = existing.scalars().all()
    declined_pairs = {(s.original_day, s.suggested_day) for s in existing_swaps if s.status == "declined"}
    pending_count = sum(1 for s in existing_swaps if s.status == "pending")

    if pending_count >= 2:
        return []

    day_scores = {}
    day_weather = {}

    for day in days:
        if day.is_locked or day.is_flex_day or day.is_arrival or day.is_departure:
            continue
        if not day.activities:
            continue

        lat, lon = _get_day_coordinates(day)
        hourly = await weather_service.get_hourly_forecast(lat, lon, days=8)

        day_date = day.date or (trip.start_date + timedelta(days=day.day_number - 1) if trip.start_date else None)
        if not day_date:
            continue

        day_hourly = [w for w in hourly if w.timestamp.date() == day_date]
        if not day_hourly:
            continue

        activity_scores = []
        for act in day.activities:
            act_types = act.attraction.types if act.attraction and act.attraction.types else ["hiking"]
            mid_weather = day_hourly[len(day_hourly) // 2] if day_hourly else None
            if mid_weather:
                report = score_activity_conditions(mid_weather, act.name, act_types)
                activity_scores.append(report.score)

        if activity_scores:
            avg_score = int(sum(activity_scores) / len(activity_scores))
            day_scores[day.day_number] = avg_score
            day_weather[day.day_number] = day_hourly

    suggestions = []
    for day_num, score in day_scores.items():
        if score >= 60:
            continue

        day_obj = next((d for d in days if d.day_number == day_num), None)
        if not day_obj:
            continue

        best_swap_day = None
        best_improvement = 0

        for other_num, other_score in day_scores.items():
            if other_num == day_num:
                continue
            if (day_num, other_num) in declined_pairs:
                continue

            other_day = next((d for d in days if d.day_number == other_num), None)
            if not other_day or other_day.is_locked:
                continue

            swap_score_forward = _estimate_cross_score(
                day_obj.activities, day_weather.get(other_num, [])
            )
            swap_score_backward = _estimate_cross_score(
                other_day.activities, day_weather.get(day_num, [])
            )

            improvement = (swap_score_forward - score) - max(0, other_score - swap_score_backward)

            if improvement > best_improvement and improvement > 15:
                best_improvement = improvement
                best_swap_day = other_num

        if best_swap_day is not None:
            disruption = _calculate_disruption(day_obj, next(d for d in days if d.day_number == best_swap_day))

            if best_improvement > 40 and disruption < 30:
                recommendation = "strong_swap"
            elif best_improvement > 25 and disruption < 50:
                recommendation = "suggest_swap"
            elif best_improvement > 15 and disruption < 20:
                recommendation = "mention_option"
            else:
                continue

            reason = await _generate_swap_reason(
                day_obj, next(d for d in days if d.day_number == best_swap_day),
                score, day_scores.get(best_swap_day, 50),
                best_improvement,
            )

            suggestion = SwapSuggestion(
                id=uuid.uuid4(),
                trip_id=trip.id,
                original_day=day_num,
                suggested_day=best_swap_day,
                reason=reason,
                improvement_score=best_improvement,
                disruption_score=disruption,
                recommendation=recommendation,
                original_conditions={
                    "score": score,
                    "assessment": score_to_assessment(score),
                },
                suggested_conditions={
                    "score": day_scores.get(best_swap_day, 50),
                    "assessment": score_to_assessment(day_scores.get(best_swap_day, 50)),
                },
                details={
                    "original_location": day_obj.location,
                    "swap_location": next(d for d in days if d.day_number == best_swap_day).location,
                },
            )
            db.add(suggestion)
            suggestions.append(suggestion)

            if len(suggestions) + pending_count >= 2:
                break

    return suggestions


def _estimate_cross_score(activities: list, weather_conditions: list) -> int:
    if not weather_conditions or not activities:
        return 50

    scores = []
    mid_weather = weather_conditions[len(weather_conditions) // 2]
    for act in activities:
        act_types = act.attraction.types if act.attraction and act.attraction.types else ["hiking"]
        report = score_activity_conditions(mid_weather, act.name, act_types)
        scores.append(report.score)

    return int(sum(scores) / len(scores)) if scores else 50


def _calculate_disruption(day_a: ItineraryDay, day_b: ItineraryDay) -> int:
    disruption = 0

    if day_a.location != day_b.location:
        disruption += 30

    for act in list(day_a.activities) + list(day_b.activities):
        if act.booking_status == "booked":
            disruption += 25

    if day_a.accommodation != day_b.accommodation:
        if day_a.accommodation.get("name") or day_b.accommodation.get("name"):
            disruption += 15

    return min(100, disruption)


async def _generate_swap_reason(
    day_a: ItineraryDay,
    day_b: ItineraryDay,
    score_a: int,
    score_b: int,
    improvement: int,
) -> str:
    try:
        prompt_input = (
            f"Day {day_a.day_number} ({day_a.location}): "
            f"Activities: {[a.name for a in day_a.activities]}, Score: {score_a}/100\n"
            f"Day {day_b.day_number} ({day_b.location}): "
            f"Activities: {[a.name for a in day_b.activities]}, Score: {score_b}/100\n"
            f"Improvement if swapped: +{improvement} points"
        )
        result = await gemini_client.generate_json(SWAP_SYSTEM_PROMPT, prompt_input)
        if result and result.get("reasoning"):
            return result["reasoning"]
    except Exception:
        log.warning("swap_reason_generation_failed")

    return (
        f"Day {day_a.day_number} has suboptimal conditions (score {score_a}/100) for your planned activities. "
        f"Swapping with Day {day_b.day_number} would improve conditions by {improvement} points."
    )


async def accept_swap(db: AsyncSession, swap: SwapSuggestion) -> bool:
    trip_result = await db.execute(
        select(Trip).where(Trip.id == swap.trip_id)
    )
    trip = trip_result.scalar_one_or_none()
    if not trip:
        return False

    days_result = await db.execute(
        select(ItineraryDay)
        .where(ItineraryDay.trip_id == swap.trip_id)
        .where(ItineraryDay.day_number.in_([swap.original_day, swap.suggested_day]))
        .options(selectinload(ItineraryDay.activities))
    )
    swap_days = {d.day_number: d for d in days_result.scalars().all()}

    day_a = swap_days.get(swap.original_day)
    day_b = swap_days.get(swap.suggested_day)
    if not day_a or not day_b:
        return False

    day_a.day_number, day_b.day_number = day_b.day_number, day_a.day_number

    if day_a.date and day_b.date:
        day_a.date, day_b.date = day_b.date, day_a.date

    swap.status = "accepted"
    return True


async def decline_swap(db: AsyncSession, swap: SwapSuggestion) -> bool:
    swap.status = "declined"
    return True


def _get_day_coordinates(day: ItineraryDay) -> tuple[float, float]:
    if day.activities:
        for act in day.activities:
            if act.attraction and act.attraction.latitude and act.attraction.longitude:
                return (act.attraction.latitude, act.attraction.longitude)

    from app.services.briefing_generator import _get_day_coordinates as _bgen_coords
    return _bgen_coords(day)
