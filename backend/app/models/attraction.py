from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Float, Integer, Boolean, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Attraction(Base):
    __tablename__ = "attractions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    activity: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    types: Mapped[list] = mapped_column(ARRAY(String), nullable=False, default=list)
    location_name: Mapped[Optional[str]] = mapped_column(String(255))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20))
    cost_level: Mapped[Optional[str]] = mapped_column(String(20))
    duration_min: Mapped[Optional[float]] = mapped_column(Float)
    duration_max: Mapped[Optional[float]] = mapped_column(Float)
    seasonal_availability: Mapped[str] = mapped_column(String(100), default="year-round")
    booking_required: Mapped[bool] = mapped_column(Boolean, default=False)
    weather_sensitivity: Mapped[str] = mapped_column(String(20), default="moderate")
    ideal_conditions: Mapped[dict] = mapped_column(JSONB, default=dict)
    acceptable_conditions: Mapped[dict] = mapped_column(JSONB, default=dict)
    dealbreaker_conditions: Mapped[dict] = mapped_column(JSONB, default=dict)
    logistics: Mapped[dict] = mapped_column(JSONB, default=dict)
    pro_tips: Mapped[list] = mapped_column(JSONB, default=list)
    uniqueness_score: Mapped[int] = mapped_column(Integer, default=50)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
