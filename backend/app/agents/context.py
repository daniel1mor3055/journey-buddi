"""PlanningContext — shared mutable state passed through the OpenAI Agents SDK.

Every agent, tool, and handoff callback receives this context via
``RunContextWrapper[PlanningContext]``.  It is serialized to the
``Conversation.planning_state`` JSONB column between turns.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class PlanningContext:
    """Cross-agent context persisted as JSONB on the Conversation model."""

    # ── Travel DNA ───────────────────────────────────────────────────────
    group_type: str | None = None
    group_details: dict[str, Any] = field(default_factory=dict)
    accessibility_needs: dict[str, Any] = field(default_factory=dict)
    fitness_profile: dict[str, Any] = field(default_factory=dict)

    # ── Logistics ────────────────────────────────────────────────────────
    destination: str | None = None
    travel_dates: dict[str, Any] = field(default_factory=dict)
    max_driving_hours: int | None = None
    flight_details: dict[str, Any] = field(default_factory=dict)

    # ── Interests (three phases) ─────────────────────────────────────────
    interest_categories: list[str] = field(default_factory=list)
    interest_details: dict[str, list[str]] = field(default_factory=dict)
    selected_providers: dict[str, dict[str, Any]] = field(default_factory=dict)

    # ── Activity-Location mapping (activity → chosen location) ────────
    activity_locations: dict[str, str] = field(default_factory=dict)

    # ── Per-location summary {location: {activities, sightseeing, recommended_days}} ─
    location_summary: dict[str, dict[str, Any]] = field(default_factory=dict)
    days_per_location: dict[str, int] = field(default_factory=dict)

    # ── Transport & Route ────────────────────────────────────────────────
    transport_plan: dict[str, Any] = field(default_factory=dict)
    route_direction: str | None = None

    # ── Pipeline state ───────────────────────────────────────────────────
    current_agent: str = "greeting"
    completed_agents: list[str] = field(default_factory=list)
    started: bool = False

    # ── Serialization ────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlanningContext:
        if not data:
            return cls()
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**copy.deepcopy(filtered))
