from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ActivityReport(BaseModel):
    activity_id: Optional[str] = None
    activity_name: str
    activity_type: str = ""
    emoji: str = "📍"
    score: int = 50
    assessment: str = "GOOD"
    confidence: str = "high"
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    key_factors: list[dict] = []
    packing_suggestions: list[str] = []
    timing_suggestion: Optional[str] = None
    pro_tips: list[str] = []


class SwapSuggestionRead(BaseModel):
    id: str
    trip_id: str
    original_day: int
    suggested_day: int
    reason: str
    improvement_score: int
    disruption_score: int
    recommendation: str
    original_conditions: dict = {}
    suggested_conditions: dict = {}
    details: dict = {}
    status: str = "pending"
    created_at: datetime

    model_config = {"from_attributes": True}


class DailyBriefingRead(BaseModel):
    id: str
    trip_id: str
    day_number: int
    briefing_date: date
    location: str
    overall_score: int
    overall_assessment: str
    confidence: str = "high"
    weather_summary: dict = {}
    solar_data: dict = {}
    activity_reports: list[dict] = []
    packing_list: list[str] = []
    timeline: list[dict] = []
    hidden_gem: Optional[str] = None
    lookahead: list[dict] = []
    ai_narrative: Optional[str] = None
    swap_suggestion: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LookaheadDay(BaseModel):
    day_number: int
    date: Optional[date] = None
    location: str = ""
    score: int = 50
    assessment: str = "GOOD"
    confidence: str = "high"
    summary: str = ""


class BriefingGenerateRequest(BaseModel):
    day_number: Optional[int] = None
    force_refresh: bool = False


class SwapActionRequest(BaseModel):
    action: str  # "accept" or "decline"
