"""Tests for the OpenAI Agents SDK-based planning system.

Tests cover:
- PlanningContext serialization
- PlanningResponse model
- All function_tools (update context + status messages)
- Pipeline wiring (agent order, handoff targets)
- Orchestrator (progress, fallbacks)
- MasterAgent prompt generation
"""
from __future__ import annotations

import pytest

from app.agents.context import PlanningContext
from app.agents.models import PlanningResponse, Choice, ProviderCardModel
from app.agents.tools import (
    travel_dna_missing,
    logistics_missing,
    interest_categories_missing,
    island_preference_missing,
    transport_route_missing,
    CANONICAL_CATEGORIES,
)
from app.agents.pipeline import (
    PIPELINE,
    AGENT_NAME_MAP,
    AGENT_TO_NAME,
    greeting_agent,
    travel_dna_agent,
    logistics_agent,
    interest_categories_agent,
    island_preference_agent,
    transport_route_agent,
)
from app.agents.orchestrator import PlanningOrchestrator
from app.agents.master import MasterAgent


# ═══════════════════════════════════════════════════════════════════════════
# PlanningContext
# ═══════════════════════════════════════════════════════════════════════════

class TestPlanningContext:
    def test_default_values(self):
        ctx = PlanningContext()
        assert ctx.group_type is None
        assert ctx.current_agent == "greeting"
        assert ctx.completed_agents == []
        assert ctx.started is False

    def test_to_dict_roundtrip(self):
        ctx = PlanningContext(
            group_type="family",
            destination="New Zealand",
            interest_categories=["Outdoor Activities", "Tours"],
            current_agent="logistics",
            completed_agents=["greeting", "travel_dna"],
        )
        d = ctx.to_dict()
        assert isinstance(d, dict)
        assert d["group_type"] == "family"
        assert d["interest_categories"] == ["Outdoor Activities", "Tours"]

        restored = PlanningContext.from_dict(d)
        assert restored.group_type == "family"
        assert restored.destination == "New Zealand"
        assert restored.completed_agents == ["greeting", "travel_dna"]

    def test_from_dict_empty(self):
        ctx = PlanningContext.from_dict({})
        assert ctx.current_agent == "greeting"
        assert ctx.group_type is None

    def test_from_dict_ignores_unknown_keys(self):
        ctx = PlanningContext.from_dict({"group_type": "solo", "unknown_field": "value"})
        assert ctx.group_type == "solo"

    def test_from_dict_none(self):
        ctx = PlanningContext.from_dict(None)
        assert ctx.current_agent == "greeting"


# ═══════════════════════════════════════════════════════════════════════════
# PlanningResponse
# ═══════════════════════════════════════════════════════════════════════════

class TestPlanningResponse:
    def test_minimal_response(self):
        r = PlanningResponse(text="Hello!")
        assert r.text == "Hello!"
        assert r.choices is None
        assert r.multi_select is False
        assert r.free_text is False

    def test_with_choices(self):
        r = PlanningResponse(
            text="Pick one",
            choices=[Choice(emoji="🎯", label="Option A", desc="desc")],
        )
        assert len(r.choices) == 1
        assert r.choices[0].label == "Option A"

    def test_with_provider_cards(self):
        r = PlanningResponse(
            text="Pick a provider",
            provider_cards=[
                ProviderCardModel(
                    emoji="🏆", name="TestCo", location="Auckland",
                    rating=4.5, reviews=100, price=200,
                    whatsSpecial="Great", buddiPick=True,
                )
            ],
        )
        assert r.provider_cards[0].buddiPick is True


# ═══════════════════════════════════════════════════════════════════════════
# Status helpers (used by tools)
# ═══════════════════════════════════════════════════════════════════════════

class TestStatusHelpers:
    def test_travel_dna_missing_all(self):
        ctx = PlanningContext()
        missing = travel_dna_missing(ctx)
        assert "group_type" in missing
        assert "accessibility_needs" in missing
        assert "fitness_profile" in missing
        assert "budget" in missing

    def test_travel_dna_missing_family_needs_count(self):
        ctx = PlanningContext(group_type="family")
        missing = travel_dna_missing(ctx)
        assert "group_count" in missing

    def test_travel_dna_missing_family_needs_ages(self):
        ctx = PlanningContext(group_type="family", group_details={"count": 4})
        missing = travel_dna_missing(ctx)
        assert "ages" in missing

    def test_travel_dna_missing_none_solo(self):
        ctx = PlanningContext(
            group_type="solo",
            group_details={"count": 1, "ages_raw": "30"},
            accessibility_needs={"level": "none"},
            fitness_profile={"general_level": "moderate"},
            budget={"level": "midrange"},
        )
        assert travel_dna_missing(ctx) == []

    def test_travel_dna_missing_none_family(self):
        ctx = PlanningContext(
            group_type="family",
            group_details={"count": 4, "ages_raw": "Adults 35, kids 8 and 5"},
            accessibility_needs={"level": "none"},
            fitness_profile={"general_level": "moderate"},
            budget={"level": "midrange"},
        )
        assert travel_dna_missing(ctx) == []

    def test_logistics_missing_all(self):
        ctx = PlanningContext()
        missing = logistics_missing(ctx)
        assert len(missing) == 3
        assert "travel_dates" in missing
        assert "trip_duration" in missing
        assert "max_driving_hours" in missing

    def test_logistics_missing_none(self):
        ctx = PlanningContext(
            travel_dates={"season": "summer"},
            trip_duration={"type": "approximate", "min_days": 12, "max_days": 16},
            max_driving_hours=4,
        )
        assert logistics_missing(ctx) == []

    def test_island_preference_missing(self):
        assert island_preference_missing(PlanningContext()) == ["island_preference"]
        ctx = PlanningContext(island_preference={"preference": "both", "islands": ["south", "north"]})
        assert island_preference_missing(ctx) == []

    def test_interest_categories_missing(self):
        assert interest_categories_missing(PlanningContext()) == ["interest_categories"]
        assert interest_categories_missing(PlanningContext(interest_categories=["Attractions"])) == []

    def test_transport_route_missing_all(self):
        assert len(transport_route_missing(PlanningContext())) == 2

    def test_transport_route_missing_none(self):
        ctx = PlanningContext(
            transport_plan={"mode": "campervan"},
            route_direction="clockwise",
        )
        assert transport_route_missing(ctx) == []


# ═══════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════

class TestConstants:
    def test_canonical_categories_count(self):
        assert len(CANONICAL_CATEGORIES) == 9

    def test_canonical_categories_have_required_keys(self):
        for cat in CANONICAL_CATEGORIES:
            assert "label" in cat
            assert "emoji" in cat
            assert "description" in cat


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline wiring
# ═══════════════════════════════════════════════════════════════════════════

class TestPipeline:
    def test_pipeline_order(self):
        names = [a.name for a in PIPELINE]
        assert names == [
            "Greeting",
            "Travel DNA",
            "Logistics",
            "Interest Categories",
            "Island Preference",
            "Transport Route",
        ]

    def test_agent_name_map_complete(self):
        assert set(AGENT_NAME_MAP.keys()) == {
            "greeting", "travel_dna", "logistics",
            "interest_categories",
            "island_preference",
            "transport_route",
        }

    def test_agent_to_name_mapping(self):
        for agent in PIPELINE:
            assert agent.name in AGENT_TO_NAME
            assert AGENT_TO_NAME[agent.name] in AGENT_NAME_MAP

    def test_all_agents_have_output_type(self):
        for agent in PIPELINE:
            assert agent.output_type is PlanningResponse, f"{agent.name} missing output_type"

    def test_no_agents_have_handoffs(self):
        """Transitions are managed by the orchestrator, not via agent handoffs."""
        for agent in PIPELINE:
            assert len(agent.handoffs) == 0, f"{agent.name} should not have handoffs"

    def test_greeting_has_tools(self):
        tool_names = [t.name for t in greeting_agent.tools]
        assert "get_tell_me_more_info" in tool_names

    def test_travel_dna_has_tools(self):
        tool_names = [t.name for t in travel_dna_agent.tools]
        assert "set_group_type" in tool_names
        assert "set_fitness_profile" in tool_names

    def test_logistics_has_tools(self):
        tool_names = [t.name for t in logistics_agent.tools]
        assert "set_travel_dates" in tool_names

    def test_all_agents_have_dynamic_instructions(self):
        for agent in PIPELINE:
            assert callable(agent.instructions), f"{agent.name} should have callable instructions"


# ═══════════════════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════════════════

class TestOrchestrator:
    def setup_method(self):
        self.orch = PlanningOrchestrator()

    def test_progress_percent_start(self):
        ctx = PlanningContext()
        assert self.orch.progress_percent(ctx) == 0.0

    def test_progress_percent_partial(self):
        ctx = PlanningContext(completed_agents=["greeting", "travel_dna"])
        pct = self.orch.progress_percent(ctx)
        assert 10 < pct < 50

    def test_progress_percent_all(self):
        ctx = PlanningContext(
            completed_agents=["greeting", "travel_dna", "logistics",
                              "interest_categories",
                              "island_preference",
                              "transport_route"],
            current_agent="complete",
        )
        assert self.orch.progress_percent(ctx) == 100.0

    def test_fallback_greeting(self):
        ctx = PlanningContext(current_agent="greeting")
        fb = self.orch._field_fallback("greeting", ctx)
        assert "text" in fb

    def test_fallback_travel_dna(self):
        ctx = PlanningContext(current_agent="travel_dna")
        fb = self.orch._field_fallback("travel_dna", ctx)
        assert fb["choices"] is not None
        assert len(fb["choices"]) == 4

    def test_fallback_interest_categories(self):
        ctx = PlanningContext(current_agent="interest_categories")
        fb = self.orch._field_fallback("interest_categories", ctx)
        assert fb["choices"] is not None
        assert len(fb["choices"]) == 9
        assert fb["multi_select"] is True

    def test_fallback_unknown_agent(self):
        ctx = PlanningContext(current_agent="nonexistent")
        fb = self.orch._field_fallback("nonexistent", ctx)
        assert "text" in fb

    def test_mark_all_complete(self):
        ctx = PlanningContext()
        self.orch._mark_all_complete(ctx)
        assert ctx.current_agent == "complete"
        assert len(ctx.completed_agents) == 6


# ═══════════════════════════════════════════════════════════════════════════
# MasterAgent
# ═══════════════════════════════════════════════════════════════════════════

class TestMasterAgent:
    def setup_method(self):
        self.master = MasterAgent()

    def test_generate_itinerary_prompt(self):
        ctx = PlanningContext(
            group_type="couple",
            group_details={"count": 2},
            accessibility_needs={"level": "none"},
            fitness_profile={"general_level": "moderate"},
            budget={"level": "midrange"},
            destination="New Zealand",
            travel_dates={"season": "summer"},
            trip_duration={"type": "approximate", "min_days": 12, "max_days": 16},
            max_driving_hours=4,
            island_preference={"preference": "both", "islands": ["south", "north"]},
            interest_categories=["Outdoor Activities", "Tours", "Attractions"],
            transport_plan={"mode": "campervan"},
            route_direction="clockwise",
        )
        prompt = self.master.generate_itinerary_prompt(ctx)
        assert "couple" in prompt
        assert "New Zealand" in prompt
        assert "Outdoor Activities" in prompt
        assert "campervan" in prompt
        assert "clockwise" in prompt
        assert "ITINERARY CONSTRAINTS" in prompt
        assert "BUDGET" in prompt
        assert "ISLAND PREFERENCE" in prompt
        assert "12-16 days" in prompt
        assert "skeleton itinerary" in prompt

    def test_generate_summary(self):
        ctx = PlanningContext(group_type="solo", destination="New Zealand")
        summary = self.master.generate_summary(ctx)
        assert summary["group"]["type"] == "solo"
        assert summary["logistics"]["destination"] == "New Zealand"

    def test_generate_summary_categories_only(self):
        ctx = PlanningContext(
            group_type="solo",
            interest_categories=["Tours", "Events"],
        )
        summary = self.master.generate_summary(ctx)
        assert summary["interests"]["categories"] == ["Tours", "Events"]
        assert "details" not in summary["interests"]
