"""Orchestrator — drives the planning conversation via the OpenAI Agents SDK.

The orchestrator manages all agent transitions (no handoffs between agents).
Each user turn runs a *single* agent with restricted tool access: only the
tool for the current missing field is available, preventing the LLM from
auto-filling multiple fields in one turn.

Tracing is enabled by default so every turn shows up in the OpenAI
dashboard for debugging.
"""
from __future__ import annotations

import os
from typing import Any

import structlog
from agents import Agent, Runner, RunConfig, ModelSettings, trace
from agents.exceptions import MaxTurnsExceeded

from app.agents.context import PlanningContext
from app.agents.models import PlanningResponse
from app.agents.pipeline import (
    PIPELINE,
    AGENT_NAME_MAP,
    AGENT_TO_NAME,
    FIELD_TOOLS,
    greeting_agent,
)
from app.agents.tools import (
    travel_dna_missing,
    logistics_missing,
    interest_categories_missing,
    interest_deep_dive_remaining,
    activity_location_remaining,
    location_summary_missing,
    provider_selection_remaining,
    transport_route_missing,
)
from app.config import get_settings

log = structlog.get_logger()

_settings = get_settings()
if _settings.openai_api_key:
    os.environ.setdefault("OPENAI_API_KEY", _settings.openai_api_key)

PIPELINE_ORDER = list(AGENT_NAME_MAP.keys())


def _build_run_config() -> RunConfig:
    return RunConfig(
        model=_settings.openai_model or "gpt-4.1-mini",
        model_settings=ModelSettings(temperature=0.7, max_tokens=2048),
    )


# ═══════════════════════════════════════════════════════════════════════════
# Domain completion checks
# ═══════════════════════════════════════════════════════════════════════════

def _agent_missing(agent_name: str, ctx: PlanningContext) -> list[str]:
    """Return the list of still-missing fields for the given agent."""
    checks: dict[str, Any] = {
        "greeting": lambda: [],
        "travel_dna": lambda: travel_dna_missing(ctx),
        "logistics": lambda: logistics_missing(ctx),
        "interest_categories": lambda: interest_categories_missing(ctx),
        "interest_deep_dive": lambda: interest_deep_dive_remaining(ctx),
        "activity_location": lambda: activity_location_remaining(ctx),
        "location_summary": lambda: location_summary_missing(ctx),
        "provider_selection": lambda: provider_selection_remaining(ctx),
        "transport_route": lambda: transport_route_missing(ctx),
    }
    fn = checks.get(agent_name)
    return fn() if fn else []


def _next_agent_name(current: str) -> str | None:
    try:
        idx = PIPELINE_ORDER.index(current)
        if idx + 1 < len(PIPELINE_ORDER):
            return PIPELINE_ORDER[idx + 1]
    except ValueError:
        pass
    return None


def _enforce_single_item(
    agent_name: str,
    ctx: PlanningContext,
    missing_before: list[str],
) -> None:
    """For dynamic agents, ensure only ONE item was filled per turn.

    If the LLM auto-filled multiple categories/activities in one run,
    keep only the first one and reset the rest.
    """
    if agent_name not in ("interest_deep_dive", "activity_location", "provider_selection"):
        return

    missing_after = _agent_missing(agent_name, ctx)
    filled = [f for f in missing_before if f not in missing_after]

    if len(filled) <= 1:
        return

    keep = filled[0]
    for item in filled[1:]:
        if agent_name == "interest_deep_dive":
            ctx.interest_details.pop(item, None)
        elif agent_name == "activity_location":
            ctx.activity_locations.pop(item, None)
        elif agent_name == "provider_selection":
            ctx.selected_providers.pop(item, None)

    log.warning(
        "auto_fill_rollback",
        agent=agent_name,
        kept=keep,
        rolled_back=filled[1:],
    )


def _restricted_agent(
    base: Agent[PlanningContext],
    agent_name: str,
    missing: list[str],
) -> Agent[PlanningContext]:
    """Create a copy of the agent with only the tool for the first missing field.

    For agents not in FIELD_TOOLS (interest_deep_dive, provider_selection)
    the full tool set is preserved since their fields are dynamic.
    """
    field_map = FIELD_TOOLS.get(agent_name)
    if not field_map or not missing:
        return base

    tools = field_map.get(missing[0], [])
    return Agent(
        name=base.name,
        instructions=base.instructions,
        tools=tools,
        output_type=PlanningResponse,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Per-field fallback questions (controlled choices the LLM cannot override)
# ═══════════════════════════════════════════════════════════════════════════

_FIELD_FALLBACKS: dict[str, dict[str, dict[str, Any]]] = {
    "travel_dna": {
        "group_type": {
            "text": "First up — who's coming along on this adventure?",
            "choices": [
                {"emoji": "🧑", "label": "Flying solo", "desc": "Just me and the open road"},
                {"emoji": "💑", "label": "With my partner", "desc": "Adventure for two"},
                {"emoji": "👨‍👩‍👧‍👦", "label": "Family trip", "desc": "Kids are coming along"},
                {"emoji": "👯", "label": "Friends trip", "desc": "The crew is rolling deep"},
            ],
        },
        "group_count": {
            "text": "How many people are in your group?",
            "choices": [
                {"emoji": "2️⃣", "label": "2", "desc": ""},
                {"emoji": "3️⃣", "label": "3", "desc": ""},
                {"emoji": "4️⃣", "label": "4", "desc": ""},
                {"emoji": "5️⃣", "label": "5", "desc": ""},
                {"emoji": "6️⃣", "label": "6+", "desc": ""},
            ],
        },
        "ages": {
            "text": "What are your ages? This helps me tailor activity difficulty and recommendations.",
            "free_text": True,
        },
        "accessibility_needs": {
            "text": "Any accessibility needs I should know about?",
            "choices": [
                {"emoji": "✅", "label": "No special needs", "desc": "All good to go"},
                {"emoji": "🚶", "label": "Prefer flat, paved paths", "desc": "Easy terrain please"},
                {"emoji": "♿", "label": "Wheelchair/stroller accessible only", "desc": "Full accessibility needed"},
            ],
        },
        "fitness_profile": {
            "text": "What's your fitness comfort zone for activities?",
            "choices": [
                {"emoji": "🌿", "label": "Keep it light", "desc": "Gentle walks and easy access"},
                {"emoji": "🥾", "label": "Up for a moderate challenge", "desc": "A few hours hiking is fine"},
                {"emoji": "⛰️", "label": "Bring on the big hikes", "desc": "Multi-hour treks, no problem"},
                {"emoji": "🎲", "label": "A mix of everything", "desc": "Some easy days, some big ones"},
            ],
        },
    },
    "logistics": {
        "travel_dates": {
            "text": "When are you thinking of visiting New Zealand?",
            "choices": [
                {"emoji": "☀️", "label": "Dec–Feb (Summer)", "desc": "Peak season, warmest weather"},
                {"emoji": "🍂", "label": "Mar–May (Autumn)", "desc": "Fewer crowds, stunning colours"},
                {"emoji": "❄️", "label": "Jun–Aug (Winter)", "desc": "Ski season, aurora chance"},
                {"emoji": "🌸", "label": "Sep–Nov (Spring)", "desc": "Blooming, shoulder season"},
                {"emoji": "🤷", "label": "Flexible", "desc": "Help me pick the best time!"},
            ],
        },
        "max_driving_hours": {
            "text": "How much driving are you comfortable with per day?",
            "choices": [
                {"emoji": "🐢", "label": "Short (1-2 hours max)", "desc": "More time at each stop"},
                {"emoji": "🚗", "label": "3-4 hours is fine", "desc": "Good balance of driving and exploring"},
                {"emoji": "🛣️", "label": "5+ hours is OK", "desc": "Happy to cover more ground"},
            ],
        },
        "flight_details": {
            "text": "Have you booked your flights to New Zealand yet?",
            "choices": [
                {"emoji": "✈️", "label": "Yes — I have details", "desc": "Ready to share arrival/departure"},
                {"emoji": "📅", "label": "Not yet — I'll add later", "desc": "Still sorting flights"},
                {"emoji": "🤔", "label": "Help me figure it out", "desc": "Need advice on flights"},
            ],
        },
    },
    "interest_categories": {
        "interest_categories": {
            "text": (
                "Now the fun part! What types of experiences get you excited? "
                "Pick everything that interests you."
            ),
            "choices": [
                {"emoji": "🏔️", "label": "Mountains & Hiking", "desc": ""},
                {"emoji": "🌊", "label": "Ocean & Marine Life", "desc": ""},
                {"emoji": "🏖️", "label": "Beaches & Coast", "desc": ""},
                {"emoji": "🌋", "label": "Volcanoes & Geothermal", "desc": ""},
                {"emoji": "🌿", "label": "Nature & Wildlife", "desc": ""},
                {"emoji": "🍷", "label": "Food & Wine", "desc": ""},
                {"emoji": "🪂", "label": "Adrenaline & Thrills", "desc": ""},
                {"emoji": "📖", "label": "Culture & History", "desc": ""},
                {"emoji": "📸", "label": "Photography & Scenery", "desc": ""},
                {"emoji": "⭐", "label": "Stargazing & Dark Skies", "desc": ""},
                {"emoji": "🚣", "label": "Water Sports", "desc": ""},
                {"emoji": "♨️", "label": "Hot Springs & Relaxation", "desc": ""},
            ],
            "multi_select": True,
        },
    },
    "transport_route": {
        "transport_mode": {
            "text": "Let's talk about getting around! How do you want to travel?",
            "choices": [
                {"emoji": "🚐", "label": "Campervan", "desc": "Freedom camping, wake up to views"},
                {"emoji": "🚗", "label": "Rental car", "desc": "Nimble, book accommodation"},
                {"emoji": "🔀", "label": "Mix of both", "desc": "Best of both worlds"},
                {"emoji": "🚌", "label": "Public transport", "desc": "Buses, trains, ferries"},
            ],
        },
        "route_direction": {
            "text": "Which direction do you want to loop around?",
            "choices": [
                {"emoji": "🔄", "label": "Clockwise", "desc": ""},
                {"emoji": "🔃", "label": "Counter-clockwise", "desc": ""},
                {"emoji": "🗺️", "label": "Custom", "desc": "Let Buddi optimise the route"},
            ],
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# Orchestrator
# ═══════════════════════════════════════════════════════════════════════════

class PlanningOrchestrator:
    """Manages the multi-agent planning conversation.

    Transitions between agents are explicit: after each successful run the
    orchestrator checks whether the current agent's domain is complete.
    If so it advances the pipeline and runs the next agent to produce its
    opening question — all within the same user turn.
    """

    def __init__(self) -> None:
        self.run_config = _build_run_config()

    # ── Public API ───────────────────────────────────────────────────────

    async def process_message(
        self,
        ctx: PlanningContext,
        user_message: str,
        conversation_history: list[dict[str, str]],
        conversation_id: str = "",
    ) -> tuple[dict[str, Any], PlanningContext]:
        agent_name = ctx.current_agent

        # Greeting is special: any message (other than "tell me more",
        # already handled by the endpoint) means "advance to travel_dna".
        if agent_name == "greeting":
            ctx.completed_agents.append("greeting")
            ctx.current_agent = "travel_dna"
            opening, ctx = await self._opening_question(ctx, conversation_history, conversation_id)
            return opening, ctx

        agent = AGENT_NAME_MAP.get(agent_name, greeting_agent)
        input_items = self._build_input(conversation_history)
        snapshot = ctx.to_dict()
        missing_before = _agent_missing(agent_name, ctx)

        log.info(
            "orchestrator_run",
            agent=agent.name,
            user_msg=user_message[:80],
            missing=missing_before,
            conversation_id=conversation_id,
        )

        try:
            run_agent = _restricted_agent(agent, agent_name, missing_before)

            with trace(
                "journey_buddi_planning",
                group_id=conversation_id or None,
                metadata={"agent": agent_name, "phase": "process_message"},
            ):
                result = await Runner.run(
                    starting_agent=run_agent,
                    input=input_items,
                    context=ctx,
                    run_config=self.run_config,
                    max_turns=10,
                )

            response = result.final_output_as(PlanningResponse)
            response_dict = response.model_dump(exclude_none=True)

            # Pipeline state is ours to manage — reset any mutations
            ctx.current_agent = agent_name
            ctx.completed_agents = list(snapshot.get("completed_agents", []))

            _enforce_single_item(agent_name, ctx, missing_before)
            missing_after = _agent_missing(agent_name, ctx)

            log.info(
                "orchestrator_field_check",
                agent=agent_name,
                missing_before=missing_before,
                missing_after=missing_after,
            )

            if not missing_after:
                # Domain complete → advance to the next agent
                response_dict, ctx = await self._advance_pipeline(
                    ctx, response_dict, conversation_history, conversation_id
                )
            else:
                # Override choices with the controlled fallback for the
                # next missing field so the LLM can't show wrong options.
                self._apply_field_choices(response_dict, agent_name, missing_after[0])

        except MaxTurnsExceeded:
            log.warning("max_turns_exceeded", agent=agent_name)
            ctx.current_agent = agent_name
            ctx.completed_agents = list(snapshot.get("completed_agents", []))

            _enforce_single_item(agent_name, ctx, missing_before)
            missing_after = _agent_missing(agent_name, ctx)
            if not missing_after:
                response_dict, ctx = await self._advance_pipeline(
                    ctx, {"text": ""}, conversation_history, conversation_id
                )
            else:
                response_dict = self._field_fallback(agent_name, ctx)

        except Exception:
            log.exception("orchestrator_error", agent=agent_name)
            ctx = PlanningContext.from_dict(snapshot)
            response_dict = self._field_fallback(agent_name, ctx)

        return response_dict, ctx

    async def init_conversation(
        self,
        ctx: PlanningContext,
        conversation_id: str = "",
    ) -> tuple[dict[str, Any], PlanningContext]:
        """Generate the opening greeting (no user input)."""
        agent = AGENT_NAME_MAP.get(ctx.current_agent, greeting_agent)

        try:
            with trace(
                "journey_buddi_planning",
                group_id=conversation_id or None,
                metadata={"agent": ctx.current_agent, "phase": "init"},
            ):
                result = await Runner.run(
                    starting_agent=agent,
                    input="Start the conversation. Greet the user warmly.",
                    context=ctx,
                    run_config=self.run_config,
                    max_turns=5,
                )

            response = result.final_output_as(PlanningResponse)
            return response.model_dump(exclude_none=True), ctx

        except Exception:
            log.exception("init_error")
            return self._field_fallback(ctx.current_agent, ctx), ctx

    def progress_percent(self, ctx: PlanningContext) -> float:
        total = len(PIPELINE)
        completed = len(ctx.completed_agents)
        if ctx.current_agent == "complete":
            return 100.0
        return round((completed / total) * 100, 1)

    # ── Pipeline transitions ─────────────────────────────────────────────

    async def _advance_pipeline(
        self,
        ctx: PlanningContext,
        current_response: dict[str, Any],
        conversation_history: list[dict[str, str]],
        conversation_id: str,
    ) -> tuple[dict[str, Any], PlanningContext]:
        """Mark the current agent complete and get the next agent's opening."""
        agent_name = ctx.current_agent
        ctx.completed_agents.append(agent_name)
        next_name = _next_agent_name(agent_name)

        if not next_name:
            ctx.current_agent = "complete"
            current_response["planning_complete"] = True
            return current_response, ctx

        ctx.current_agent = next_name
        ack_text = current_response.get("text", "")

        opening, ctx = await self._opening_question(
            ctx, conversation_history, conversation_id
        )

        if ack_text:
            opening["text"] = ack_text + "\n\n" + opening.get("text", "")

        log.info(
            "pipeline_advance",
            from_agent=agent_name,
            to_agent=next_name,
            completed=ctx.completed_agents,
        )
        return opening, ctx

    async def _opening_question(
        self,
        ctx: PlanningContext,
        conversation_history: list[dict[str, str]],
        conversation_id: str,
    ) -> tuple[dict[str, Any], PlanningContext]:
        """Run the current agent with NO tools to produce its first question.

        Tools are withheld so the LLM cannot auto-fill data from the
        synthetic "I'm ready for the next step" prompt.
        """
        agent_name = ctx.current_agent
        agent = AGENT_NAME_MAP.get(agent_name, greeting_agent)
        missing = _agent_missing(agent_name, ctx)

        try:
            input_items = self._build_input(conversation_history)
            input_items.append({
                "role": "user",
                "content": "I'm ready for the next step.",
            })

            question_only_agent = Agent(
                name=agent.name,
                instructions=agent.instructions,
                tools=[],
                output_type=PlanningResponse,
            )

            with trace(
                "journey_buddi_planning",
                group_id=conversation_id or None,
                metadata={"agent": agent_name, "phase": "opening_question"},
            ):
                result = await Runner.run(
                    starting_agent=question_only_agent,
                    input=input_items,
                    context=ctx,
                    run_config=self.run_config,
                    max_turns=3,
                )

            response = result.final_output_as(PlanningResponse)
            response_dict = response.model_dump(exclude_none=True)

            if missing:
                self._apply_field_choices(response_dict, agent_name, missing[0])

            return response_dict, ctx

        except Exception:
            log.exception("opening_question_error", agent=agent_name)
            return self._field_fallback(agent_name, ctx), ctx

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _build_input(conversation_history: list[dict[str, str]]) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        for msg in conversation_history[-30:]:
            role = "user" if msg["role"] == "user" else "assistant"
            items.append({"role": role, "content": msg["content"]})
        return items

    @staticmethod
    def _apply_field_choices(
        response_dict: dict[str, Any],
        agent_name: str,
        field: str,
    ) -> None:
        """Override the response's choices with the controlled fallback."""
        agent_fields = _FIELD_FALLBACKS.get(agent_name, {})
        fallback = agent_fields.get(field)
        if fallback:
            if "choices" in fallback:
                response_dict["choices"] = fallback["choices"]
            response_dict["multi_select"] = fallback.get("multi_select", False)
            response_dict["free_text"] = fallback.get("free_text", False)
            if fallback.get("free_text"):
                response_dict.pop("choices", None)

    @staticmethod
    def _field_fallback(agent_name: str, ctx: PlanningContext) -> dict[str, Any]:
        """Return the per-field fallback for the first missing field."""
        missing = _agent_missing(agent_name, ctx)
        agent_fields = _FIELD_FALLBACKS.get(agent_name, {})

        if missing and missing[0] in agent_fields:
            fb = agent_fields[missing[0]]
            return {
                "text": fb.get("text", "Let's continue!"),
                "choices": fb.get("choices"),
                "multi_select": fb.get("multi_select", False),
                "free_text": fb.get("free_text", False),
            }

        if agent_name == "interest_deep_dive" and missing:
            from app.agents.tools import ACTIVITY_OPTIONS
            category = missing[0]
            options = ACTIVITY_OPTIONS.get(category, [])
            if options:
                choices = [
                    {"emoji": "✅", "label": opt, "desc": ""}
                    for opt in options
                ]
                return {
                    "text": f"Let's explore **{category}**! Which activities appeal to you?",
                    "choices": choices,
                    "multi_select": True,
                    "free_text": False,
                }
            return {
                "text": f"What specific **{category}** activities interest you?",
                "choices": None,
                "multi_select": False,
                "free_text": True,
            }

        if agent_name == "activity_location" and missing:
            activity = missing[0]
            from app.agents.tools import ACTIVITY_LOCATION_MAP
            options = ACTIVITY_LOCATION_MAP.get(activity, [])
            if options:
                choices = [
                    {
                        "emoji": "📍",
                        "label": f"{opt['location']} — {opt['name']}",
                        "desc": opt.get("highlight", ""),
                    }
                    for opt in options
                ]
                return {
                    "text": f"Where would you like to do **{activity}**?",
                    "choices": choices,
                    "multi_select": False,
                    "free_text": False,
                }
            return {
                "text": f"Where in New Zealand would you like to do **{activity}**?",
                "choices": None,
                "multi_select": False,
                "free_text": True,
            }

        if agent_name == "location_summary" and missing:
            return {
                "text": (
                    "Let me put together your per-location plan — "
                    "grouping activities, recommending days, and suggesting bonus sightseeing."
                ),
                "choices": None,
                "multi_select": False,
                "free_text": True,
            }

        if agent_name == "provider_selection" and missing:
            activity = missing[0]
            return {
                "text": (
                    f"Let me find providers for **{activity}**. "
                    "I'll suggest a few options from different regions of New Zealand."
                ),
                "choices": None,
                "multi_select": False,
                "free_text": True,
            }

        return {
            "text": "Let me think about that — could you try again?",
            "choices": None,
            "multi_select": False,
            "free_text": False,
        }

    @staticmethod
    def _mark_all_complete(ctx: PlanningContext) -> None:
        for agent in PIPELINE:
            name = AGENT_TO_NAME.get(agent.name, "")
            if name and name not in ctx.completed_agents:
                ctx.completed_agents.append(name)
        ctx.current_agent = "complete"


def transport_route_has_missing(ctx: PlanningContext) -> bool:
    return bool(transport_route_missing(ctx))


orchestrator = PlanningOrchestrator()
