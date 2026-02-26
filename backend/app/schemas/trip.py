from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TripCreate(BaseModel):
    destination: str
    destination_region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    entry_point: Optional[str] = None
    exit_point: Optional[str] = None


class TripUpdate(BaseModel):
    destination: Optional[str] = None
    destination_region: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    entry_point: Optional[str] = None
    exit_point: Optional[str] = None
    transport_plan: Optional[dict] = None
    flight_details: Optional[dict] = None
    planning_state: Optional[dict] = None


class TripRead(BaseModel):
    id: UUID
    user_id: UUID
    destination: str
    destination_region: Optional[str] = None
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    entry_point: Optional[str] = None
    exit_point: Optional[str] = None
    transport_plan: dict = {}
    flight_details: dict = {}
    planning_state: dict = {}
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
