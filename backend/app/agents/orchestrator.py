"""Orchestrator — drives the planning conversation via the OpenAI Agents SDK.

Each user turn triggers a single ``Runner.run()`` call.  The SDK handles
tool execution, structured output, and agent handoffs automatically.
Tracing is enabled by default so every turn shows up in the OpenAI
dashboard for debugging.
"""
from __future__ import annotations

import os
from typing import Any

import structlog
from agents import Runner, RunConfig, ModelSettings, trace
from agents.exceptions import MaxTurnsExceeded

from app.agents.context import PlanningContext
from app.agents.models import PlanningResponse
from app.agents.pipeline import (
    PIPELINE,
    AGENT_NAME_MAP,
    AGENT_TO_NAME,
    greeting_agent,
)
from app.config import get_settings

log = structlog.get_logger()

# Ensure the SDK can find the API key loaded from .env by pydantic-settings
_settings = get_settings()
if _settings.openai_api_key:
    os.environ.setdefault("OPENAI_API_KEY", _settings.openai_api_key)


def _build_run_config() -> RunConfig:
    """Global RunConfig applied to every Runner.run() call."""
    return RunConfig(
        model=_settings.openai_model or "gpt-4o-mini",
        model_settings=ModelSettings(temperature=0.7, max_tokens=2048),
    )


# ═══════════════════════════════════════════════════════════════════════════

_FALLBACK_RESPONSES: dict[str, dict[str, Any]] = {
    "greeting": {
        "text": (
            "Hey there! 👋 I'm Buddi, your travel companion. I'm going to help you "
            "plan an incredible New Zealand adventure — one that adapts to conditions, "
            "saves you money, and shows you things most tourists miss.\n\n"
            "Let's start by getting to know your travel style. This takes about "
            "10 minutes and saves you 20+ hours of research. Ready?"
        ),
        "choices": [
            {"emoji": "🎯", "label": "Let's do it!", "desc": "Start planning your trip"},
            {"emoji": "🗺️", "label": "Tell me more first", "desc": "Learn what Journey Buddi can do"},
        ],
    },
    "travel_dna": {
        "text": "First up — who's coming along on this adventure?",
        "choices": [
            {"emoji": "🧑", "label": "Flying solo", "desc": "Just me and the open road"},
            {"emoji": "💑", "label": "With my partner", "desc": "Adventure for two"},
            {"emoji": "👨‍👩‍👧‍👦", "label": "Family trip", "desc": "Kids are coming along"},
            {"emoji": "👯", "label": "Friends trip", "desc": "The crew is rolling deep"},
        ],
    },
    "logistics": {
        "text": "Now let's sort out the logistics! When are you thinking of visiting New Zealand?",
        "choices": [
            {"emoji": "☀️", "label": "Dec–Feb (Summer)", "desc": "Peak season, warmest weather"},
            {"emoji": "🍂", "label": "Mar–May (Autumn)", "desc": "Fewer crowds, stunning colours"},
            {"emoji": "❄️", "label": "Jun–Aug (Winter)", "desc": "Ski season, aurora chance"},
            {"emoji": "🌸", "label": "Sep–Nov (Spring)", "desc": "Blooming, shoulder season"},
            {"emoji": "🤷", "label": "Flexible", "desc": "Help me pick the best time!"},
        ],
    },
    "interest_categories": {
        "text": (
            "Now the fun part! What types of experiences get you excited? "
            "Pick everything that interests you — I'll find the best options."
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
    "interest_deep_dive": {
        "text": (
            "Let's dig deeper into what excites you! "
            "I'll show you activity types for each category — pick everything that appeals."
        ),
        "multi_select": True,
        "free_text": True,
    },
    "provider_selection": {
        "text": (
            "Time to find the best operators for your activities! "
            "I'll show you options from across New Zealand."
        ),
    },
    "transport_route": {
        "text": "Let's talk about getting around! How do you want to travel?",
        "choices": [
            {"emoji": "🚐", "label": "Campervan", "desc": "Freedom camping, wake up to views"},
            {"emoji": "🚗", "label": "Rental car", "desc": "Nimble, book accommodation"},
            {"emoji": "🔀", "label": "Mix of both", "desc": "Best of both worlds"},
            {"emoji": "🚌", "label": "Public transport", "desc": "Buses, trains, ferries"},
        ],
    },
}


class PlanningOrchestrator:
    """Manages the multi-agent planning conversation using the OpenAI Agents SDK."""

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
        """Handle one user turn and return ``(ai_response_dict, updated_ctx)``."""
        agent = AGENT_NAME_MAP.get(ctx.current_agent, greeting_agent)

        input_items = self._build_input(conversation_history)

        log.info(
            "orchestrator_run",
            agent=agent.name,
            user_msg=user_message[:80],
            conversation_id=conversation_id,
        )

        snapshot = ctx.to_dict()

        try:
            with trace(
                "journey_buddi_planning",
                group_id=conversation_id or None,
                metadata={"agent": ctx.current_agent, "phase": "process_message"},
            ):
                result = await Runner.run(
                    starting_agent=agent,
                    input=input_items,
                    context=ctx,
                    run_config=self.run_config,
                    max_turns=8,
                )

            response = result.final_output_as(PlanningResponse)
            response_dict = response.model_dump(exclude_none=True)

            last_agent_name = AGENT_TO_NAME.get(result.last_agent.name, ctx.current_agent)
            ctx.current_agent = last_agent_name

            if last_agent_name == "transport_route" and not transport_route_has_missing(ctx):
                self._mark_all_complete(ctx)
                response_dict["planning_complete"] = True

            log.info(
                "orchestrator_done",
                current_agent=ctx.current_agent,
                completed=ctx.completed_agents,
            )

        except MaxTurnsExceeded:
            log.warning("max_turns_exceeded", agent=agent.name)
            ctx = self._restore_safe(ctx, snapshot)
            response_dict = self._fallback(ctx)

        except Exception:
            log.exception("orchestrator_error", agent=agent.name)
            ctx = self._restore_safe(ctx, snapshot)
            response_dict = self._fallback(ctx)

        return response_dict, ctx

    async def init_conversation(
        self,
        ctx: PlanningContext,
        conversation_id: str = "",
    ) -> tuple[dict[str, Any], PlanningContext]:
        """Generate the opening message (no real user input)."""
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
            return self._fallback(ctx), ctx

    def progress_percent(self, ctx: PlanningContext) -> float:
        total = len(PIPELINE)
        completed = len(ctx.completed_agents)
        if ctx.current_agent == "complete":
            return 100.0
        return round((completed / total) * 100, 1)

    # ── Private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _build_input(conversation_history: list[dict[str, str]]) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        for msg in conversation_history[-30:]:
            role = "user" if msg["role"] == "user" else "assistant"
            items.append({"role": role, "content": msg["content"]})
        return items

    @staticmethod
    def _restore_safe(
        mutated_ctx: PlanningContext,
        snapshot: dict[str, Any],
    ) -> PlanningContext:
        """Restore context from snapshot, allowing at most one pipeline advance.

        If the run completed the starting agent (one legitimate handoff), we
        keep that single advance so the fallback shows the correct next step.
        Any further cascading mutations are rolled back.
        """
        original_agent = snapshot["current_agent"]
        original_completed = set(snapshot.get("completed_agents", []))
        new_completed = set(mutated_ctx.completed_agents) - original_completed

        restored = PlanningContext.from_dict(snapshot)

        if len(new_completed) >= 1 and original_agent in mutated_ctx.completed_agents:
            pipeline_names = list(AGENT_NAME_MAP.keys())
            try:
                idx = pipeline_names.index(original_agent)
                if idx + 1 < len(pipeline_names):
                    restored.completed_agents.append(original_agent)
                    restored.current_agent = pipeline_names[idx + 1]
            except ValueError:
                pass

        return restored

    @staticmethod
    def _fallback(ctx: PlanningContext) -> dict[str, Any]:
        base = _FALLBACK_RESPONSES.get(ctx.current_agent, _FALLBACK_RESPONSES["greeting"])
        return {
            "text": base.get("text", "Let me think about that — could you try again?"),
            "choices": base.get("choices"),
            "multi_select": base.get("multi_select", False),
            "free_text": base.get("free_text", False),
            "provider_cards": base.get("provider_cards"),
        }

    @staticmethod
    def _mark_all_complete(ctx: PlanningContext) -> None:
        for agent in PIPELINE:
            name = AGENT_TO_NAME.get(agent.name, "")
            if name and name not in ctx.completed_agents:
                ctx.completed_agents.append(name)
        ctx.current_agent = "complete"


def transport_route_has_missing(ctx: PlanningContext) -> bool:
    from app.agents.tools import transport_route_missing
    return bool(transport_route_missing(ctx))


orchestrator = PlanningOrchestrator()
