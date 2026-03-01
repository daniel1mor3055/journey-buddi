from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class ItineraryActivityRead(BaseModel):
    id: UUID
    itinerary_day_id: UUID
    attraction_id: Optional[UUID] = None
    name: str
    emoji: str = "📍"
    provider: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    price: float = 0
    currency: str = "NZD"
    booking_status: str = "not-booked"
    booking_ref: Optional[str] = None
    condition_score: Optional[int] = None
    notes: Optional[str] = None
    sort_order: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ItineraryDayRead(BaseModel):
    id: UUID
    trip_id: UUID
    day_number: int
    date: Optional[date] = None
    location: str
    title: Optional[str] = None
    summary: Optional[str] = None
    is_flex_day: bool = False
    is_arrival: bool = False
    is_departure: bool = False
    is_locked: bool = False
    accommodation: dict = {}
    transport: dict = {}
    weather: dict = {}
    notes: Optional[str] = None
    activities: List[ItineraryActivityRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ItineraryDayUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    is_locked: Optional[bool] = None
    is_flex_day: Optional[bool] = None
    accommodation: Optional[dict] = None
    transport: Optional[dict] = None
    notes: Optional[str] = None


class ItinerarySwapRequest(BaseModel):
    day_a: int
    day_b: int


class ItineraryOverview(BaseModel):
    trip_id: UUID
    total_days: int
    total_activities: int
    booked_count: int
    needs_booking_count: int
    flex_days: int
    days: List[ItineraryDayRead]
