from __future__ import annotations

from typing import Optional

import structlog

from app.schemas.conditions import (
    WeatherCondition,
    ActivityConditionReport,
    DayConditionReport,
)

log = structlog.get_logger()

ASSESSMENT_LEVELS = {
    (80, 101): "EXCELLENT",
    (60, 80): "GOOD",
    (40, 60): "FAIR",
    (20, 40): "POOR",
    (0, 20): "UNSAFE",
}


def score_to_assessment(score: int) -> str:
    for (lo, hi), label in ASSESSMENT_LEVELS.items():
        if lo <= score < hi:
            return label
    return "UNSAFE"


ACTIVITY_CONDITION_PROFILES = {
    "hiking": {
        "conditions": [
            {"param": "wind_speed_kmh", "ideal": (0, 25), "acceptable": (0, 45), "deal_breaker": 65, "weight": 0.25},
            {"param": "precipitation_probability_pct", "ideal": (0, 15), "acceptable": (0, 45), "deal_breaker": None, "weight": 0.25},
            {"param": "temperature_c", "ideal": (5, 22), "acceptable": (-5, 30), "deal_breaker": None, "weight": 0.15},
            {"param": "visibility_km", "ideal": (10, 100), "acceptable": (3, 100), "deal_breaker": 0.5, "weight": 0.2},
            {"param": "cloud_cover_pct", "ideal": (0, 40), "acceptable": (0, 80), "deal_breaker": None, "weight": 0.15},
        ],
    },
    "alpine_hiking": {
        "conditions": [
            {"param": "wind_speed_kmh", "ideal": (0, 20), "acceptable": (0, 40), "deal_breaker": 60, "weight": 0.3},
            {"param": "precipitation_probability_pct", "ideal": (0, 10), "acceptable": (0, 40), "deal_breaker": None, "weight": 0.2},
            {"param": "visibility_km", "ideal": (15, 100), "acceptable": (5, 100), "deal_breaker": 1, "weight": 0.25},
            {"param": "temperature_c", "ideal": (0, 18), "acceptable": (-10, 25), "deal_breaker": None, "weight": 0.1},
            {"param": "cloud_cover_pct", "ideal": (0, 30), "acceptable": (0, 70), "deal_breaker": None, "weight": 0.15},
        ],
    },
    "water_activity": {
        "conditions": [
            {"param": "wind_speed_kmh", "ideal": (0, 15), "acceptable": (0, 30), "deal_breaker": 50, "weight": 0.35},
            {"param": "precipitation_probability_pct", "ideal": (0, 10), "acceptable": (0, 40), "deal_breaker": None, "weight": 0.2},
            {"param": "temperature_c", "ideal": (12, 28), "acceptable": (5, 35), "deal_breaker": None, "weight": 0.15},
            {"param": "cloud_cover_pct", "ideal": (0, 40), "acceptable": (0, 80), "deal_breaker": None, "weight": 0.15},
            {"param": "visibility_km", "ideal": (5, 100), "acceptable": (2, 100), "deal_breaker": None, "weight": 0.15},
        ],
    },
    "scenic": {
        "conditions": [
            {"param": "cloud_cover_pct", "ideal": (0, 25), "acceptable": (0, 60), "deal_breaker": None, "weight": 0.35},
            {"param": "visibility_km", "ideal": (20, 100), "acceptable": (5, 100), "deal_breaker": 1, "weight": 0.3},
            {"param": "precipitation_probability_pct", "ideal": (0, 10), "acceptable": (0, 40), "deal_breaker": None, "weight": 0.2},
            {"param": "wind_speed_kmh", "ideal": (0, 25), "acceptable": (0, 50), "deal_breaker": None, "weight": 0.15},
        ],
    },
    "wildlife": {
        "conditions": [
            {"param": "wind_speed_kmh", "ideal": (0, 20), "acceptable": (0, 40), "deal_breaker": None, "weight": 0.25},
            {"param": "precipitation_probability_pct", "ideal": (0, 20), "acceptable": (0, 50), "deal_breaker": None, "weight": 0.25},
            {"param": "temperature_c", "ideal": (5, 25), "acceptable": (-5, 35), "deal_breaker": None, "weight": 0.15},
            {"param": "visibility_km", "ideal": (5, 100), "acceptable": (1, 100), "deal_breaker": None, "weight": 0.2},
            {"param": "cloud_cover_pct", "ideal": (0, 60), "acceptable": (0, 90), "deal_breaker": None, "weight": 0.15},
        ],
    },
    "geothermal": {
        "conditions": [
            {"param": "precipitation_probability_pct", "ideal": (0, 30), "acceptable": (0, 70), "deal_breaker": None, "weight": 0.3},
            {"param": "temperature_c", "ideal": (5, 25), "acceptable": (-5, 35), "deal_breaker": None, "weight": 0.25},
            {"param": "wind_speed_kmh", "ideal": (0, 30), "acceptable": (0, 50), "deal_breaker": None, "weight": 0.2},
            {"param": "visibility_km", "ideal": (3, 100), "acceptable": (1, 100), "deal_breaker": None, "weight": 0.25},
        ],
    },
    "indoor": {
        "conditions": [
            {"param": "temperature_c", "ideal": (-20, 40), "acceptable": (-30, 50), "deal_breaker": None, "weight": 0.5},
            {"param": "precipitation_probability_pct", "ideal": (0, 100), "acceptable": (0, 100), "deal_breaker": None, "weight": 0.5},
        ],
    },
    "stargazing": {
        "conditions": [
            {"param": "cloud_cover_pct", "ideal": (0, 10), "acceptable": (0, 30), "deal_breaker": 80, "weight": 0.5},
            {"param": "visibility_km", "ideal": (20, 100), "acceptable": (10, 100), "deal_breaker": 5, "weight": 0.3},
            {"param": "wind_speed_kmh", "ideal": (0, 15), "acceptable": (0, 30), "deal_breaker": None, "weight": 0.2},
        ],
    },
}

ATTRACTION_TYPE_TO_PROFILE = {
    "hiking": "hiking",
    "trekking": "alpine_hiking",
    "alpine": "alpine_hiking",
    "kayaking": "water_activity",
    "surfing": "water_activity",
    "snorkeling": "water_activity",
    "boat": "water_activity",
    "marine": "water_activity",
    "swimming": "water_activity",
    "scenic": "scenic",
    "viewpoint": "scenic",
    "photography": "scenic",
    "glacier": "scenic",
    "wildlife": "wildlife",
    "birdwatching": "wildlife",
    "whale_watching": "wildlife",
    "geothermal": "geothermal",
    "hot_springs": "geothermal",
    "museum": "indoor",
    "cultural": "indoor",
    "food": "indoor",
    "stargazing": "stargazing",
    "aurora": "stargazing",
    "adventure": "hiking",
    "nature": "hiking",
    "beach": "scenic",
    "coastal": "scenic",
}


def _resolve_profile(activity_types: list[str]) -> str:
    for t in activity_types:
        t_lower = t.lower().replace(" ", "_").replace("-", "_")
        if t_lower in ATTRACTION_TYPE_TO_PROFILE:
            return ATTRACTION_TYPE_TO_PROFILE[t_lower]
    return "hiking"


def _score_parameter(value: float, ideal: tuple, acceptable: tuple, deal_breaker: Optional[float]) -> int:
    if deal_breaker is not None:
        if isinstance(deal_breaker, (int, float)):
            if ideal[0] <= ideal[1]:
                if value >= deal_breaker:
                    return -1
            else:
                if value <= deal_breaker:
                    return -1

    lo_i, hi_i = ideal
    lo_a, hi_a = acceptable

    if lo_i <= value <= hi_i:
        mid = (lo_i + hi_i) / 2
        dist = abs(value - mid) / ((hi_i - lo_i) / 2) if (hi_i - lo_i) > 0 else 0
        return int(100 - dist * 20)

    if lo_a <= value <= hi_a:
        if value < lo_i:
            range_size = lo_i - lo_a
            dist = (lo_i - value) / range_size if range_size > 0 else 1
        else:
            range_size = hi_a - hi_i
            dist = (value - hi_i) / range_size if range_size > 0 else 1
        return int(79 - dist * 40)

    if value < lo_a:
        dist = lo_a - value
        return max(0, int(39 - dist * 5))
    else:
        dist = value - hi_a
        return max(0, int(39 - dist * 5))


def score_activity_conditions(
    weather: WeatherCondition,
    activity_name: str,
    activity_types: list[str],
    confidence: str = "high",
) -> ActivityConditionReport:
    profile_name = _resolve_profile(activity_types)
    profile = ACTIVITY_CONDITION_PROFILES.get(profile_name, ACTIVITY_CONDITION_PROFILES["hiking"])

    total_score = 0.0
    total_weight = 0.0
    has_dealbreaker = False
    key_factors = []

    for cond in profile["conditions"]:
        param = cond["param"]
        value = getattr(weather, param, None)
        if value is None:
            continue

        param_score = _score_parameter(value, cond["ideal"], cond["acceptable"], cond["deal_breaker"])

        if param_score == -1:
            has_dealbreaker = True
            key_factors.append({
                "parameter": param,
                "value": value,
                "score": 0,
                "note": f"Deal-breaker: {param}={value} exceeds safe limit",
            })
            continue

        weighted = param_score * cond["weight"]
        total_score += weighted
        total_weight += cond["weight"]

        if param_score < 60:
            key_factors.append({
                "parameter": param,
                "value": value,
                "score": param_score,
                "note": f"{param}: {value} (below ideal range)",
            })

    if has_dealbreaker:
        final_score = 0
    elif total_weight > 0:
        final_score = int(total_score / total_weight)
    else:
        final_score = 50

    if confidence == "medium":
        if final_score < 40:
            final_score = max(final_score, 40)
        if final_score > 80:
            final_score = min(final_score, 80)
    elif confidence == "low":
        final_score = max(40, min(final_score, 70))

    assessment = "UNSAFE" if has_dealbreaker else score_to_assessment(final_score)

    packing = _generate_packing_suggestions(weather, profile_name)

    return ActivityConditionReport(
        activity_name=activity_name,
        activity_type=profile_name,
        score=final_score,
        assessment=assessment,
        confidence=confidence,
        key_factors=key_factors,
        packing_suggestions=packing,
    )


def _generate_packing_suggestions(weather: WeatherCondition, profile: str) -> list[str]:
    suggestions = []

    if weather.precipitation_probability_pct > 30:
        suggestions.append("Rain jacket / waterproof layer")
    if weather.temperature_c < 10:
        suggestions.append("Warm layers (fleece + insulation)")
    if weather.temperature_c < 5:
        suggestions.append("Gloves and beanie")
    if weather.wind_speed_kmh > 25:
        suggestions.append("Windproof jacket")
    if weather.uv_index and weather.uv_index > 5:
        suggestions.append("Sunscreen SPF50+, sunglasses, hat")
    elif weather.uv_index and weather.uv_index > 3:
        suggestions.append("Sunscreen and sunglasses")
    if profile in ("hiking", "alpine_hiking"):
        suggestions.append("Water bottle (2L+ recommended)")
        suggestions.append("Comfortable hiking shoes")
    if profile == "water_activity":
        suggestions.append("Quick-dry clothing / swimwear")
        if weather.temperature_c < 18:
            suggestions.append("Wetsuit or thermal rash guard")

    return suggestions


def score_day_conditions(
    weather_conditions: list[WeatherCondition],
    activities: list[dict],
    day_number: int,
    day_date: Optional[str] = None,
    location: str = "",
    confidence: str = "high",
) -> DayConditionReport:
    activity_reports = []

    for act in activities:
        act_name = act.get("name", "Activity")
        act_types = act.get("types", ["hiking"])
        time_start = act.get("time_start")

        best_weather = None
        if time_start and weather_conditions:
            target_hour = int(time_start.split(":")[0]) if ":" in str(time_start) else 12
            best_weather = min(
                weather_conditions,
                key=lambda w: abs(w.timestamp.hour - target_hour),
            )
        elif weather_conditions:
            mid_conditions = [w for w in weather_conditions if 8 <= w.timestamp.hour <= 18]
            best_weather = mid_conditions[len(mid_conditions) // 2] if mid_conditions else weather_conditions[0]

        if best_weather:
            report = score_activity_conditions(best_weather, act_name, act_types, confidence)
            report.activity_id = act.get("id")
            activity_reports.append(report)

    if activity_reports:
        overall_score = int(sum(r.score for r in activity_reports) / len(activity_reports))
    else:
        overall_score = 50

    overall_assessment = score_to_assessment(overall_score)

    weather_summary = None
    if weather_conditions:
        day_temps = [w.temperature_c for w in weather_conditions]
        weather_summary = {
            "temp_min": round(min(day_temps), 1),
            "temp_max": round(max(day_temps), 1),
            "avg_wind": round(sum(w.wind_speed_kmh for w in weather_conditions) / len(weather_conditions), 1),
            "max_precip_prob": round(max(w.precipitation_probability_pct for w in weather_conditions), 1),
            "avg_cloud": round(sum(w.cloud_cover_pct for w in weather_conditions) / len(weather_conditions), 1),
            "description": weather_conditions[len(weather_conditions) // 2].description,
        }

    from datetime import date as date_cls
    parsed_date = date_cls.fromisoformat(day_date) if day_date else None

    return DayConditionReport(
        day_number=day_number,
        date=parsed_date,
        location=location,
        overall_score=overall_score,
        overall_assessment=overall_assessment,
        confidence=confidence,
        weather_summary=weather_summary,
        activity_reports=activity_reports,
    )
