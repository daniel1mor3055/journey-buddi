from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Text, Date, DateTime, Float, Integer, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[Optional[date]] = mapped_column(Date)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    is_flex_day: Mapped[bool] = mapped_column(Boolean, default=False)
    is_arrival: Mapped[bool] = mapped_column(Boolean, default=False)
    is_departure: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    accommodation: Mapped[dict] = mapped_column(JSONB, default=dict)
    transport: Mapped[dict] = mapped_column(JSONB, default=dict)
    weather: Mapped[dict] = mapped_column(JSONB, default=dict)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trip = relationship("Trip", back_populates="itinerary_days")
    activities = relationship(
        "ItineraryActivity",
        back_populates="itinerary_day",
        cascade="all, delete-orphan",
        order_by="ItineraryActivity.sort_order",
    )


class ItineraryActivity(Base):
    __tablename__ = "itinerary_activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_day_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("itinerary_days.id"), nullable=False, index=True
    )
    attraction_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("attractions.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    emoji: Mapped[str] = mapped_column(String(10), default="📍")
    provider: Mapped[Optional[str]] = mapped_column(String(255))
    time_start: Mapped[Optional[str]] = mapped_column(String(10))
    time_end: Mapped[Optional[str]] = mapped_column(String(10))
    price: Mapped[float] = mapped_column(Float, default=0)
    currency: Mapped[str] = mapped_column(String(10), default="NZD")
    booking_status: Mapped[str] = mapped_column(String(20), default="not-booked")
    booking_ref: Mapped[Optional[str]] = mapped_column(String(100))
    condition_score: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    itinerary_day = relationship("ItineraryDay", back_populates="activities")
    attraction = relationship("Attraction")
