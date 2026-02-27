from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel


class WeatherCondition(BaseModel):
    timestamp: datetime
    location_lat: float
    location_lon: float
    provider: str

    temperature_c: float
    feels_like_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_kmh: float
    wind_direction_deg: int
    wind_gust_kmh: float
    precipitation_probability_pct: float
    precipitation_intensity_mmh: float = 0.0
    precipitation_type: Optional[str] = None
    cloud_cover_pct: float
    visibility_km: float
    uv_index: Optional[float] = None
    description: str = ""
    icon: str = "unknown"


class DailyWeatherSummary(BaseModel):
    date: date
    temp_min_c: float
    temp_max_c: float
    description: str
    icon: str
    precipitation_probability_pct: float
    wind_speed_max_kmh: float
    uv_index_max: Optional[float] = None
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    moon_phase: Optional[float] = None


class SolarCondition(BaseModel):
    date: date
    location_lat: float
    location_lon: float

    sunrise: datetime
    sunset: datetime
    solar_noon: Optional[datetime] = None
    day_length_hours: float
    civil_dawn: Optional[datetime] = None
    civil_dusk: Optional[datetime] = None

    golden_hour_morning_start: Optional[datetime] = None
    golden_hour_morning_end: Optional[datetime] = None
    golden_hour_evening_start: Optional[datetime] = None
    golden_hour_evening_end: Optional[datetime] = None

    moon_phase: Optional[float] = None
    moon_phase_name: Optional[str] = None
    moon_illumination_pct: Optional[float] = None


class ConditionScore(BaseModel):
    score: int
    assessment: str
    confidence: str = "high"
    confidence_reason: str = ""
    details: dict = {}


class ActivityConditionReport(BaseModel):
    activity_id: Optional[str] = None
    activity_name: str
    activity_type: str
    score: int
    assessment: str
    confidence: str = "high"
    key_factors: list[dict] = []
    packing_suggestions: list[str] = []
    timing_suggestion: Optional[str] = None


class DayConditionReport(BaseModel):
    day_number: int
    date: Optional[date] = None
    location: str
    overall_score: int
    overall_assessment: str
    confidence: str = "high"
    weather_summary: Optional[dict] = None
    solar: Optional[dict] = None
    activity_reports: list[ActivityConditionReport] = []


class ConditionForecastResponse(BaseModel):
    trip_id: str
    generated_at: datetime
    days: list[DayConditionReport] = []


class CurrentConditionsResponse(BaseModel):
    lat: float
    lon: float
    weather: Optional[WeatherCondition] = None
    solar: Optional[SolarCondition] = None
    fetched_at: datetime
