from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.briefing import DailyBriefing
from app.models.itinerary import ItineraryDay, ItineraryActivity
from app.models.trip import Trip
from app.services.weather import weather_service
from app.services.solar import solar_service
from app.services.condition_scorer import score_activity_conditions, score_to_assessment
from app.services.openai_client import openai_client as gemini_client

log = structlog.get_logger()

BRIEFING_SYSTEM_PROMPT = """You are Buddi, an expert New Zealand travel companion. Generate a concise, warm daily briefing.

You will receive:
- Day details (location, activities, weather conditions)
- Condition scores for each activity

Generate a JSON response with these fields:
{
  "greeting": "A warm 1-sentence morning greeting mentioning the location",
  "overall_message": "1-2 sentences summarizing the day's outlook based on conditions",
  "activity_tips": [
    {
      "activity_name": "...",
      "tip": "1-2 specific tips for this activity given today's conditions",
      "timing_suggestion": "Suggested optimal time if relevant"
    }
  ],
  "hidden_gem": "One bonus recommendation near today's area that isn't in the itinerary (1-2 sentences)",
  "packing_additions": ["Any extra items to pack beyond the standard list"],
  "timeline": [
    {"time": "7:00 AM", "activity": "Wake up, breakfast"},
    {"time": "8:30 AM", "activity": "Depart for first activity"}
  ]
}

Be specific, actionable, and personable. Reference actual weather numbers (temp, wind). Keep each field concise."""


async def generate_briefing_for_day(
    db: AsyncSession,
    trip: Trip,
    day: ItineraryDay,
) -> DailyBriefing:
    activities_data = []
    if day.activities:
        for act in day.activities:
            act_data = {
                "id": str(act.id),
                "name": act.name,
                "emoji": act.emoji,
                "types": [],
                "time_start": act.time_start,
                "time_end": act.time_end,
                "provider": act.provider,
            }
            if act.attraction:
                act_data["types"] = act.attraction.types or []
            elif act.notes:
                act_data["types"] = ["hiking"]
            else:
                act_data["types"] = ["scenic"]
            activities_data.append(act_data)

    lat, lon = _get_day_coordinates(day)

    hourly_weather = await weather_service.get_hourly_forecast(lat, lon, days=3)
    daily_weather = await weather_service.get_daily_forecast(lat, lon, days=5)

    briefing_date = day.date or (trip.start_date + timedelta(days=day.day_number - 1) if trip.start_date else date.today())
    day_weather = [
        w for w in hourly_weather
        if w.timestamp.date() == briefing_date
    ]

    solar = await solar_service.get_solar(lat, lon, briefing_date)

    activity_reports = []
    all_packing = set()

    for act_data in activities_data:
        target_hour = 12
        if act_data.get("time_start") and ":" in str(act_data["time_start"]):
            target_hour = int(act_data["time_start"].split(":")[0])

        weather_for_activity = None
        if day_weather:
            weather_for_activity = min(
                day_weather,
                key=lambda w: abs(w.timestamp.hour - target_hour),
            )
        elif hourly_weather:
            weather_for_activity = hourly_weather[0]

        if weather_for_activity:
            report = score_activity_conditions(
                weather_for_activity,
                act_data["name"],
                act_data["types"],
            )
            activity_reports.append({
                "activity_id": act_data["id"],
                "activity_name": act_data["name"],
                "emoji": act_data["emoji"],
                "score": report.score,
                "assessment": report.assessment,
                "confidence": report.confidence,
                "key_factors": report.key_factors,
                "packing_suggestions": report.packing_suggestions,
                "time_start": act_data.get("time_start"),
                "time_end": act_data.get("time_end"),
            })
            all_packing.update(report.packing_suggestions)

            act_obj = next((a for a in day.activities if str(a.id) == act_data["id"]), None)
            if act_obj:
                act_obj.condition_score = report.score

    if activity_reports:
        overall_score = int(sum(r["score"] for r in activity_reports) / len(activity_reports))
    else:
        overall_score = 50

    overall_assessment = score_to_assessment(overall_score)

    weather_summary = {}
    if day_weather:
        temps = [w.temperature_c for w in day_weather]
        weather_summary = {
            "temp_min": round(min(temps), 1),
            "temp_max": round(max(temps), 1),
            "description": day_weather[len(day_weather) // 2].description,
            "icon": day_weather[len(day_weather) // 2].icon,
            "avg_wind_kmh": round(sum(w.wind_speed_kmh for w in day_weather) / len(day_weather), 1),
            "max_precip_prob": round(max(w.precipitation_probability_pct for w in day_weather), 1),
        }
    elif daily_weather:
        for dw in daily_weather:
            if dw.date == briefing_date:
                weather_summary = {
                    "temp_min": dw.temp_min_c,
                    "temp_max": dw.temp_max_c,
                    "description": dw.description,
                    "icon": dw.icon,
                    "max_precip_prob": dw.precipitation_probability_pct,
                    "avg_wind_kmh": dw.wind_speed_max_kmh,
                }
                break

    solar_data = {}
    if solar:
        solar_data = {
            "sunrise": solar.sunrise.isoformat() if solar.sunrise else None,
            "sunset": solar.sunset.isoformat() if solar.sunset else None,
            "day_length_hours": solar.day_length_hours,
            "golden_morning_start": solar.golden_hour_morning_start.isoformat() if solar.golden_hour_morning_start else None,
            "golden_evening_start": solar.golden_hour_evening_start.isoformat() if solar.golden_hour_evening_start else None,
            "moon_phase_name": solar.moon_phase_name,
            "moon_illumination_pct": solar.moon_illumination_pct,
        }

    lookahead = []
    for dw in daily_weather:
        if dw.date and dw.date > briefing_date:
            days_ahead = (dw.date - briefing_date).days
            if days_ahead <= 5:
                conf = "high" if days_ahead <= 2 else ("medium" if days_ahead <= 4 else "low")
                rough_score = 80
                if dw.precipitation_probability_pct > 60:
                    rough_score -= 25
                if dw.wind_speed_max_kmh > 40:
                    rough_score -= 15
                rough_score = max(20, min(100, rough_score))
                lookahead.append({
                    "date": dw.date.isoformat(),
                    "score": rough_score,
                    "assessment": score_to_assessment(rough_score),
                    "confidence": conf,
                    "summary": dw.description,
                    "temp_range": f"{dw.temp_min_c:.0f}-{dw.temp_max_c:.0f}°C",
                })

    ai_narrative = None
    timeline = []
    hidden_gem = None
    try:
        ai_input = (
            f"Day {day.day_number} in {day.location}.\n"
            f"Weather: {weather_summary}\n"
            f"Activities: {[{r['activity_name']: r['assessment']} for r in activity_reports]}\n"
            f"Overall score: {overall_score}/100 ({overall_assessment})\n"
        )
        ai_result = await gemini_client.generate_json(
            BRIEFING_SYSTEM_PROMPT,
            ai_input,
        )
        if ai_result:
            ai_narrative = ai_result.get("greeting", "") + " " + ai_result.get("overall_message", "")
            hidden_gem = ai_result.get("hidden_gem")
            timeline = ai_result.get("timeline", [])
            for tip in ai_result.get("activity_tips", []):
                for report in activity_reports:
                    if report["activity_name"] == tip.get("activity_name"):
                        report["timing_suggestion"] = tip.get("timing_suggestion")
                        report["pro_tips"] = [tip.get("tip", "")]
            packing_additions = ai_result.get("packing_additions", [])
            all_packing.update(packing_additions)
    except Exception:
        log.warning("ai_briefing_generation_failed")

    briefing = DailyBriefing(
        id=uuid.uuid4(),
        trip_id=trip.id,
        day_number=day.day_number,
        briefing_date=briefing_date,
        location=day.location,
        overall_score=overall_score,
        overall_assessment=overall_assessment,
        weather_summary=weather_summary,
        solar_data=solar_data,
        activity_reports=activity_reports,
        packing_list=sorted(all_packing),
        timeline=timeline,
        hidden_gem=hidden_gem,
        lookahead=lookahead,
        ai_narrative=ai_narrative,
    )

    db.add(briefing)
    return briefing


def _get_day_coordinates(day: ItineraryDay) -> tuple[float, float]:
    NZ_LOCATION_COORDS = {
        "christchurch": (-43.53, 172.63),
        "queenstown": (-45.03, 168.66),
        "milford sound": (-44.67, 167.93),
        "kaikoura": (-42.40, 173.68),
        "abel tasman": (-40.90, 173.00),
        "aoraki": (-43.73, 170.10),
        "mount cook": (-43.73, 170.10),
        "tekapo": (-44.00, 170.48),
        "wanaka": (-44.70, 169.13),
        "dunedin": (-45.87, 170.50),
        "franz josef": (-43.39, 170.18),
        "fox glacier": (-43.47, 170.02),
        "rotorua": (-38.14, 176.25),
        "taupo": (-38.69, 176.08),
        "tongariro": (-39.28, 175.56),
        "wellington": (-41.29, 174.78),
        "auckland": (-36.85, 174.76),
        "coromandel": (-36.76, 175.50),
        "bay of islands": (-35.23, 174.09),
        "nelson": (-41.27, 173.28),
        "marlborough": (-41.51, 173.95),
        "fiordland": (-45.42, 167.72),
        "stewart island": (-46.90, 168.13),
        "hokitika": (-42.45, 170.97),
        "punakaiki": (-42.11, 171.33),
        "oamaru": (-45.10, 170.97),
        "invercargill": (-46.41, 168.35),
        "new zealand": (-41.29, 174.78),
    }

    if day.activities:
        for act in day.activities:
            if act.attraction and act.attraction.latitude and act.attraction.longitude:
                return (act.attraction.latitude, act.attraction.longitude)

    location_lower = day.location.lower()
    for name, coords in NZ_LOCATION_COORDS.items():
        if name in location_lower:
            return coords

    return (-41.29, 174.78)
