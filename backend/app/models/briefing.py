from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Text, Date, DateTime, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DailyBriefing(Base):
    __tablename__ = "daily_briefings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, index=True
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    briefing_date: Mapped[date] = mapped_column(Date, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)

    overall_score: Mapped[int] = mapped_column(Integer, default=50)
    overall_assessment: Mapped[str] = mapped_column(String(20), default="GOOD")
    confidence: Mapped[str] = mapped_column(String(20), default="high")

    weather_summary: Mapped[dict] = mapped_column(JSONB, default=dict)
    solar_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    activity_reports: Mapped[list] = mapped_column(JSONB, default=list)
    packing_list: Mapped[list] = mapped_column(JSONB, default=list)
    timeline: Mapped[list] = mapped_column(JSONB, default=list)
    hidden_gem: Mapped[Optional[str]] = mapped_column(Text)
    lookahead: Mapped[list] = mapped_column(JSONB, default=list)
    ai_narrative: Mapped[Optional[str]] = mapped_column(Text)

    swap_suggestion: Mapped[Optional[dict]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trip = relationship("Trip")


class SwapSuggestion(Base):
    __tablename__ = "swap_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False, index=True
    )
    original_day: Mapped[int] = mapped_column(Integer, nullable=False)
    suggested_day: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    improvement_score: Mapped[int] = mapped_column(Integer, default=0)
    disruption_score: Mapped[int] = mapped_column(Integer, default=0)
    recommendation: Mapped[str] = mapped_column(String(30), default="suggest_swap")
    original_conditions: Mapped[dict] = mapped_column(JSONB, default=dict)
    suggested_conditions: Mapped[dict] = mapped_column(JSONB, default=dict)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)

    status: Mapped[str] = mapped_column(String(20), default="pending")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    trip = relationship("Trip")
