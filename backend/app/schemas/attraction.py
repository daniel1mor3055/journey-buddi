from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class AttractionRead(BaseModel):
    id: UUID
    destination: str
    region: Optional[str] = None
    name: str
    slug: str
    description: Optional[str] = None
    types: List[str] = []
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    difficulty: Optional[str] = None
    cost_level: Optional[str] = None
    duration_min: Optional[float] = None
    duration_max: Optional[float] = None
    seasonal_availability: str = "year-round"
    booking_required: bool = False
    weather_sensitivity: str = "moderate"
    ideal_conditions: dict = {}
    acceptable_conditions: dict = {}
    dealbreaker_conditions: dict = {}
    logistics: dict = {}
    pro_tips: list = []
    uniqueness_score: int = 50
    metadata_: dict = {}
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AttractionSummary(BaseModel):
    id: UUID
    name: str
    slug: str
    types: List[str] = []
    location_name: Optional[str] = None
    difficulty: Optional[str] = None
    cost_level: Optional[str] = None
    uniqueness_score: int = 50
    description: Optional[str] = None

    model_config = {"from_attributes": True}
