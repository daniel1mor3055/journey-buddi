"""MasterAgent — generates a comprehensive itinerary prompt from PlanningContext.

This is NOT a conversation agent.  It runs once after all conversation agents
are satisfied and produces a verbose, structured prompt that feeds the
itinerary generation pipeline.

After the 3-level activity design shift the conversation only collects
*categories* (Level 1).  Specific activities (Level 2) and providers
(Level 3) are chosen post-chat, so those fields will be empty here.
The prompt still has placeholders so the itinerary generator knows
activities and providers will be filled in later.
"""
from __future__ import annotations

import json
from typing import Any

from app.agents.context import PlanningContext


class MasterAgent:
    """Synthesises all collected preferences into an itinerary-generation prompt."""

    name = "master"
    display_name = "Itinerary Architect"

    def generate_itinerary_prompt(self, ctx: PlanningContext) -> str:
        sections: list[str] = [
            "You are an expert itinerary planner for Journey Buddi.  Using the "
            "traveler profile below, create a detailed day-by-day itinerary.\n",
        ]

        sections.append(self._section("TRAVELER GROUP", self._group_section(ctx)))
        sections.append(self._section("FITNESS & ACCESSIBILITY", self._fitness_section(ctx)))
        sections.append(self._section("BUDGET", self._budget_section(ctx)))
        sections.append(self._section("LOGISTICS", self._logistics_section(ctx)))
        sections.append(self._section("ISLAND PREFERENCE", self._island_section(ctx)))
        sections.append(self._section("INTEREST CATEGORIES", self._interests_section(ctx)))
        sections.append(self._section("ACTIVITIES & PROVIDERS (post-chat)", self._providers_section(ctx)))
        sections.append(self._section("TRANSPORT & ROUTE", self._transport_section(ctx)))
        sections.append(self._constraints_section(ctx))

        return "\n".join(sections)

    def generate_summary(self, ctx: PlanningContext) -> dict[str, Any]:
        return {
            "group": {
                "type": ctx.group_type,
                "details": ctx.group_details,
            },
            "fitness": ctx.fitness_profile,
            "accessibility": ctx.accessibility_needs,
            "budget": ctx.budget,
            "logistics": {
                "destination": ctx.destination,
                "dates": ctx.travel_dates,
                "trip_duration": ctx.trip_duration,
                "max_driving_hours": ctx.max_driving_hours,
            },
            "island_preference": ctx.island_preference,
            "interests": {
                "categories": ctx.interest_categories,
            },
            "transport": ctx.transport_plan,
            "route": ctx.route_direction,
        }

    @staticmethod
    def _section(title: str, body: str) -> str:
        return f"## {title}\n{body}\n"

    @staticmethod
    def _group_section(ctx: PlanningContext) -> str:
        lines = [f"- Group type: {ctx.group_type or 'unknown'}"]
        if ctx.group_details:
            lines.append(f"- Details: {json.dumps(ctx.group_details, default=str)}")
        return "\n".join(lines)

    @staticmethod
    def _fitness_section(ctx: PlanningContext) -> str:
        lines: list[str] = []
        if ctx.fitness_profile:
            lines.append(f"- Fitness profile: {json.dumps(ctx.fitness_profile, default=str)}")
        if ctx.accessibility_needs:
            lines.append(f"- Accessibility: {json.dumps(ctx.accessibility_needs, default=str)}")
        return "\n".join(lines) if lines else "- No specific constraints"

    @staticmethod
    def _budget_section(ctx: PlanningContext) -> str:
        if ctx.budget:
            return f"- Budget level: {ctx.budget.get('level', 'not specified')}"
        return "- No budget preference specified"

    @staticmethod
    def _island_section(ctx: PlanningContext) -> str:
        if ctx.island_preference:
            pref = ctx.island_preference.get("preference", "both")
            islands = ctx.island_preference.get("islands", [])
            notes = ctx.island_preference.get("notes", "")
            line = f"- Island preference: {pref} ({', '.join(islands)})"
            if notes:
                line += f"\n- Notes: {notes}"
            return line
        return "- Both islands (no specific preference)"

    @staticmethod
    def _logistics_section(ctx: PlanningContext) -> str:
        lines = [
            f"- Destination: {ctx.destination or 'New Zealand'}",
            f"- Dates: {json.dumps(ctx.travel_dates, default=str) if ctx.travel_dates else 'flexible'}",
            f"- Trip duration: {json.dumps(ctx.trip_duration, default=str) if ctx.trip_duration else 'flexible'}",
            f"- Max driving per day: {ctx.max_driving_hours or 'not specified'} hours",
        ]
        return "\n".join(lines)

    @staticmethod
    def _interests_section(ctx: PlanningContext) -> str:
        if not ctx.interest_categories:
            return "- None specified"
        lines = [f"- {cat}" for cat in ctx.interest_categories]
        lines.append("\nNote: Specific activities within these categories will be "
                      "chosen by the traveler post-chat (Level 2).")
        return "\n".join(lines)

    @staticmethod
    def _providers_section(ctx: PlanningContext) -> str:
        return ("- Activities and providers are selected post-chat.\n"
                "- Generate a skeleton itinerary with location slots; the traveler\n"
                "  will fill in specific activities and providers progressively.")

    @staticmethod
    def _transport_section(ctx: PlanningContext) -> str:
        lines: list[str] = []
        if ctx.transport_plan:
            lines.append(f"- Transport: {json.dumps(ctx.transport_plan, default=str)}")
        if ctx.route_direction:
            lines.append(f"- Route direction: {ctx.route_direction}")
        return "\n".join(lines) if lines else "- No transport preferences specified"

    @staticmethod
    def _constraints_section(ctx: PlanningContext) -> str:
        lines = [
            "## ITINERARY CONSTRAINTS",
            "- Optimise the route to minimise backtracking.",
            "- Spread activities geographically — don't cluster everything in one area.",
            "- Include flex/rest days proportional to trip length.",
            "- Balance hard and easy days based on the fitness profile.",
            "- Account for accessibility needs in every day's plan.",
            f"- Maximum driving per day: {ctx.max_driving_hours or 4} hours.",
            "- Include accommodation suggestions appropriate for the transport mode.",
            "- Note weather-sensitive activities and suggest optimal timing.",
        ]
        if ctx.island_preference:
            islands = ctx.island_preference.get("islands", [])
            if set(islands) != {"south", "north"}:
                lines.append(f"- Restrict itinerary to: {', '.join(i.title() + ' Island' for i in islands)}.")
            else:
                lines.append("- Include inter-island ferry/flight in the route plan.")
        duration = ctx.trip_duration
        if duration:
            dtype = duration.get("type", "")
            if dtype == "fixed" and duration.get("days"):
                lines.append(f"- HARD CONSTRAINT: Trip must fit within {duration['days']} days.")
            elif dtype == "approximate":
                min_d = duration.get("min_days", "?")
                max_d = duration.get("max_days", "?")
                lines.append(f"- Target trip length: {min_d}-{max_d} days.")
        if ctx.budget:
            level = ctx.budget.get("level", "")
            if level == "budget":
                lines.append("- Prefer free/low-cost activities and budget accommodation.")
            elif level == "premium":
                lines.append("- Include premium experiences and quality accommodation.")
        return "\n".join(lines) + "\n"
