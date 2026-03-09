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
    island_preference_missing,
    activity_location_remaining,
    location_summary_missing,
    provider_selection_remaining,
    transport_route_missing,
    GROUP_TYPE_ALIASES,
    ACCESSIBILITY_ALIASES,
    FITNESS_ALIASES,
    BUDGET_ALIASES,
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
        "island_preference": lambda: island_preference_missing(ctx),
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
            "text": "Does anyone in your group have accessibility requirements?",
            "choices": [
                {"emoji": "✅", "label": "No accessibility needs", "desc": "No restrictions — full range of activities"},
                {"emoji": "🍼", "label": "Travelling with stroller/pram", "desc": "Need pram-friendly paths, accommodation & vehicles"},
                {"emoji": "♿", "label": "Wheelchair or mobility aid", "desc": "Need fully accessible facilities throughout"},
            ],
        },
        "fitness_profile": {
            "text": "To help me pace our days perfectly, let's talk about your energy levels. What does a comfortable day of exploring look like for you?",
            "choices": [
                {"emoji": "🛋️", "label": "Keep it relaxed", "desc": "Scenic drives, flat strolls, frequent stops. Up to an hour of walking a day."},
                {"emoji": "🥾", "label": "Active explorer", "desc": "A few hours on my feet — towns, beaches, gentle hills. Need time to recharge."},
                {"emoji": "🔥", "label": "Endless energy", "desc": "Steep climbs, full-day excursions — bring it on."},
                {"emoji": "🎲", "label": "A mix of everything", "desc": "Push occasionally, balanced with easy recovery days."},
            ],
        },
        "budget": {
            "text": "Last thing — what's your rough budget comfort zone per person?",
            "choices": [
                {"emoji": "🏷️", "label": "Budget-friendly", "desc": "Free/cheap activities, keep costs low"},
                {"emoji": "💵", "label": "Mid-range", "desc": "Happy to pay for great experiences"},
                {"emoji": "💎", "label": "Treat ourselves", "desc": "Premium experiences, no stress about cost"},
                {"emoji": "🤷", "label": "Flexible", "desc": "Depends on the experience"},
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
        "trip_duration": {
            "text": "How much time do you have for New Zealand?",
            "choices": [
                {"emoji": "📅", "label": "About a week", "desc": "7-10 days"},
                {"emoji": "🗓️", "label": "About 2 weeks", "desc": "12-16 days"},
                {"emoji": "📆", "label": "About 3 weeks", "desc": "18-23 days"},
                {"emoji": "🌏", "label": "A month or more", "desc": "25+ days"},
                {"emoji": "🤷", "label": "I'm flexible", "desc": "Help me figure out the right length"},
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
    "island_preference": {
        "island_preference": {
            "text": (
                "New Zealand has two main islands, each with its own character. "
                "Which would you like to explore?"
            ),
            "choices": [
                {"emoji": "🏔️", "label": "South Island", "desc": "Mountains, glaciers, fjords — the adventure hub"},
                {"emoji": "🌋", "label": "North Island", "desc": "Volcanoes, geothermal, Māori culture, beaches"},
                {"emoji": "🗺️", "label": "Both islands", "desc": "The full NZ experience"},
            ],
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
            elif missing_after == missing_before:
                # LLM made zero progress (no tool was called).  First try to
                # resolve the user message directly against the known alias
                # tables so the conversation can advance without an extra
                # round-trip.  If resolution succeeds we show the next field's
                # fallback question; if it fails we re-show the current one.
                log.warning(
                    "orchestrator_no_progress",
                    agent=agent_name,
                    stuck_on=missing_after[0],
                )
                if self._try_direct_fill(agent_name, missing_after[0], user_message, ctx):
                    log.info(
                        "orchestrator_direct_fill",
                        agent=agent_name,
                        field=missing_after[0],
                        value=user_message,
                    )
                    missing_after = _agent_missing(agent_name, ctx)
                    if not missing_after:
                        response_dict, ctx = await self._advance_pipeline(
                            ctx, response_dict, conversation_history, conversation_id
                        )
                    else:
                        response_dict = self._field_fallback(agent_name, ctx)
                else:
                    response_dict = self._field_fallback(agent_name, ctx)
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

    # ── Alias tables for every controlled-choice step ─────────────────────
    # These mirror the fallback choices in _FIELD_FALLBACKS so we can
    # resolve button clicks directly if the LLM skips the tool call.
    _TRAVEL_DATE_ALIASES: dict[str, dict] = {
        "dec–feb (summer)": {"season": "summer"},
        "mar–may (autumn)": {"season": "autumn"},
        "jun–aug (winter)": {"season": "winter"},
        "sep–nov (spring)": {"season": "spring"},
        "flexible": {"flexibility": "flexible"},
    }
    _TRIP_DURATION_ALIASES: dict[str, dict] = {
        "about a week": {"type": "approximate", "min_days": 7, "max_days": 10},
        "about 2 weeks": {"type": "approximate", "min_days": 12, "max_days": 16},
        "about 3 weeks": {"type": "approximate", "min_days": 18, "max_days": 23},
        "a month or more": {"type": "approximate", "min_days": 25, "max_days": 60},
        "i'm flexible": {"type": "flexible"},
    }
    _MAX_DRIVING_ALIASES: dict[str, int] = {
        "short (1-2 hours max)": 2,
        "3-4 hours is fine": 4,
        "5+ hours is ok": 5,
    }
    _ISLAND_ALIASES: dict[str, str] = {
        "south island": "south_only",
        "north island": "north_only",
        "both islands": "both",
        "south": "south_only",
        "north": "north_only",
        "both": "both",
    }
    _TRANSPORT_MODE_ALIASES: dict[str, str] = {
        "campervan": "campervan",
        "rental car": "car",
        "mix of both": "mix",
        "public transport": "public",
    }
    _ROUTE_DIRECTION_ALIASES: dict[str, str] = {
        "clockwise": "clockwise",
        "counter-clockwise": "counter-clockwise",
        "custom": "custom",
        "let buddi optimise the route": "custom",
    }

    @staticmethod
    def _try_direct_fill(agent_name: str, field: str, user_message: str, ctx: PlanningContext) -> bool:
        """Resolve a controlled-choice button label directly without an LLM call.

        When the LLM skips a tool call for a field that has a known alias table,
        we can resolve the user's button selection ourselves and update the context.
        Returns True if the field was successfully filled, False otherwise.
        """
        msg = user_message.strip().lower()
        inst = PlanningOrchestrator

        if agent_name == "travel_dna":
            if field == "group_type":
                normalized = GROUP_TYPE_ALIASES.get(msg)
                if normalized:
                    ctx.group_type = normalized
                    if normalized == "solo":
                        ctx.group_details = {"count": 1}
                    elif normalized == "couple":
                        ctx.group_details = {"count": 2}
                    return True

            elif field == "accessibility_needs":
                level = ACCESSIBILITY_ALIASES.get(msg)
                if level is not None:
                    ctx.accessibility_needs = {"level": level, "notes": ""}
                    return True

            elif field == "fitness_profile":
                alias_result = FITNESS_ALIASES.get(msg)
                if alias_result:
                    level_key, can_high_exertion = alias_result
                    ctx.fitness_profile = {
                        "general_level": level_key,
                        "can_handle_high_exertion": can_high_exertion,
                        "notes": "",
                    }
                    return True

            elif field == "budget":
                level = BUDGET_ALIASES.get(msg)
                if level is not None:
                    ctx.budget = {"level": level, "notes": ""}
                    return True

        elif agent_name == "logistics":
            if field == "travel_dates":
                dates = inst._TRAVEL_DATE_ALIASES.get(msg)
                if dates:
                    ctx.travel_dates = dates
                    if not ctx.destination:
                        ctx.destination = "New Zealand"
                    return True

            elif field == "trip_duration":
                duration = inst._TRIP_DURATION_ALIASES.get(msg)
                if duration:
                    ctx.trip_duration = duration
                    return True

            elif field == "max_driving_hours":
                hours = inst._MAX_DRIVING_ALIASES.get(msg)
                if hours is not None:
                    ctx.max_driving_hours = hours
                    return True

        elif agent_name == "interest_categories":
            if field == "interest_categories":
                # Multi-select: user message is comma-separated category labels
                cats = [c.strip() for c in user_message.split(",") if c.strip()]
                if cats:
                    ctx.interest_categories = cats
                    return True

        elif agent_name == "interest_deep_dive":
            # field == category name; user message is comma-separated activity labels
            activities = [a.strip() for a in user_message.split(",") if a.strip()]
            if activities:
                ctx.interest_details[field] = activities
                return True

        elif agent_name == "island_preference":
            if field == "island_preference":
                normalized = inst._ISLAND_ALIASES.get(msg)
                if normalized:
                    islands_map = {
                        "south_only": ["south"],
                        "north_only": ["north"],
                        "both": ["south", "north"],
                    }
                    ctx.island_preference = {
                        "preference": normalized,
                        "islands": islands_map.get(normalized, ["south", "north"]),
                        "notes": "",
                    }
                    return True

        elif agent_name == "activity_location":
            # field = activity name; user message = chosen location string.
            # Any non-empty value is valid — we mirror exactly what set_activity_location does.
            location = user_message.strip()
            if location:
                ctx.activity_locations[field] = location
                return True

        elif agent_name == "provider_selection":
            # field = activity name; user message = chosen provider name.
            # Mirror set_provider behaviour: store a provider dict directly.
            provider = user_message.strip()
            if provider:
                ctx.selected_providers[field] = {
                    "name": provider,
                    "location": "",
                    "notes": "",
                }
                return True

        elif agent_name == "transport_route":
            if field == "transport_mode":
                mode = inst._TRANSPORT_MODE_ALIASES.get(msg)
                if mode:
                    ctx.transport_plan = {"mode": mode, "details": ""}
                    return True

            elif field == "route_direction":
                direction = inst._ROUTE_DIRECTION_ALIASES.get(msg)
                if direction:
                    ctx.route_direction = direction
                    return True

        return False

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
