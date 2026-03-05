from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.itinerary import ItineraryDay, ItineraryActivity
from app.models.briefing import DailyBriefing
from app.models.trip import Trip
from app.services.openai_client import openai_client as gemini_client
from app.services.weather import weather_service

log = structlog.get_logger()

COMPANION_SYSTEM_PROMPT = """You are Buddi, an expert New Zealand travel companion. The trip is now ACTIVE — the traveler is currently on their trip.

CONTEXT:
You have access to the current itinerary, today's conditions, the traveler's preferences,
and REAL PRO TIPS from experienced travelers for each activity.

PERSONALITY:
- Warm, knowledgeable, practical
- Speak like a well-traveled friend riding along
- Be specific with recommendations (times, places, distances)
- Reference actual conditions when relevant
- Use the pro tips provided — they are real, verified advice

CAPABILITIES:
- Answer questions about today's plan and conditions
- Suggest adjustments if conditions change — provide specific backup alternatives
- Provide activity tips and hidden gems from the knowledge base
- Help with logistics (directions, parking, food, nearest facilities)
- Warn about logistics gaps (no food, no cell coverage, road conditions)
- Share booking reminders and preparation tips
- Suggest backup plans when weather doesn't cooperate

RULES:
- Keep responses concise and actionable
- Reference real weather data when discussing conditions
- Use the PRO TIPS provided for each activity — these are real, tested tips
- If conditions are poor for an activity, suggest a specific backup from the knowledge base
- Always mention logistics warnings (food gaps, parking, cell coverage)
- Always prioritize safety

Respond as plain text (not JSON) — this is a free-form chat, not structured planning."""


async def generate_companion_response(
    db: AsyncSession,
    trip: Trip,
    user_message: str,
    conversation_history: Optional[list] = None,
) -> str:
    today = date.today()
    current_day_number = None
    if trip.start_date:
        delta = (today - trip.start_date).days + 1
        if delta > 0:
            current_day_number = delta

    itinerary_context = ""
    conditions_context = ""

    if current_day_number:
        day_result = await db.execute(
            select(ItineraryDay)
            .where(ItineraryDay.trip_id == trip.id, ItineraryDay.day_number == current_day_number)
            .options(selectinload(ItineraryDay.activities).selectinload(ItineraryActivity.attraction))
        )
        today_day = day_result.scalar_one_or_none()

        if today_day:
            activities_text = []
            pro_tips_context = ""
            logistics_context = ""
            for act in today_day.activities:
                time_str = f" at {act.time_start}" if act.time_start else ""
                activities_text.append(f"- {act.emoji} {act.name}{time_str}")

                if act.attraction:
                    tips = act.attraction.pro_tips or []
                    if tips:
                        tip_lines = [f"  [{t.get('category', '')}] {t.get('tip', '')}" for t in tips[:8]]
                        pro_tips_context += f"\nPRO TIPS for {act.name}:\n" + "\n".join(tip_lines)

                    att_logistics = act.attraction.logistics or {}
                    warnings = []
                    if att_logistics.get("parking"):
                        warnings.append(f"Parking: {att_logistics['parking']}")
                    if att_logistics.get("food_nearby"):
                        warnings.append(f"Food: {att_logistics['food_nearby']}")
                    if att_logistics.get("cell_coverage") and att_logistics["cell_coverage"] != "good":
                        warnings.append(f"Cell coverage: {att_logistics['cell_coverage']}")
                    if att_logistics.get("access"):
                        warnings.append(f"Access: {att_logistics['access']}")
                    if act.attraction.booking_required:
                        warnings.append("BOOKING REQUIRED — traveler should have confirmation ready")
                    if warnings:
                        logistics_context += f"\nLOGISTICS for {act.name}:\n" + "\n".join(f"  - {w}" for w in warnings)

            itinerary_context = (
                f"\nTODAY'S PLAN (Day {current_day_number}):\n"
                f"Location: {today_day.location}\n"
                f"Activities:\n" + "\n".join(activities_text)
                + pro_tips_context
                + logistics_context
            )

            if today_day.activities:
                first_act = today_day.activities[0]
                lat, lon = None, None
                if first_act.attraction and first_act.attraction.latitude:
                    lat = first_act.attraction.latitude
                    lon = first_act.attraction.longitude

                if lat and lon:
                    weather = await weather_service.get_conditions_for_datetime(
                        lat, lon, datetime.now(timezone.utc)
                    )
                    if weather:
                        conditions_context = (
                            f"\nCURRENT CONDITIONS ({today_day.location}):\n"
                            f"Temperature: {weather.temperature_c}°C (feels like {weather.feels_like_c}°C)\n"
                            f"Wind: {weather.wind_speed_kmh} km/h\n"
                            f"Cloud cover: {weather.cloud_cover_pct}%\n"
                            f"Rain probability: {weather.precipitation_probability_pct}%\n"
                            f"Description: {weather.description}\n"
                        )

        briefing_result = await db.execute(
            select(DailyBriefing)
            .where(DailyBriefing.trip_id == trip.id, DailyBriefing.day_number == current_day_number)
            .order_by(DailyBriefing.created_at.desc())
            .limit(1)
        )
        briefing = briefing_result.scalar_one_or_none()
        if briefing:
            conditions_context += (
                f"\nTODAY'S BRIEFING ASSESSMENT: {briefing.overall_assessment} "
                f"(score: {briefing.overall_score}/100)\n"
            )

    trip_context = (
        f"\nTRIP INFO:\n"
        f"Destination: {trip.destination}\n"
        f"Status: {trip.status}\n"
        f"Start: {trip.start_date}\n"
        f"End: {trip.end_date}\n"
    )

    preferences = trip.planning_state or {}
    if preferences:
        trip_context += f"Preferences: {json.dumps({k: v for k, v in preferences.items() if k != 'current_step'})}\n"

    full_system = (
        COMPANION_SYSTEM_PROMPT
        + trip_context
        + itinerary_context
        + conditions_context
    )

    response = await gemini_client.generate(
        system_prompt=full_system,
        user_message=user_message,
        conversation_history=conversation_history,
        temperature=0.7,
    )

    return response
