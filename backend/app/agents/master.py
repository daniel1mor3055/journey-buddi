"""MasterAgent — generates a comprehensive itinerary prompt from PlanningContext.

This is NOT a conversation agent.  It runs once after all conversation agents
are satisfied and produces a verbose, structured prompt that feeds the
itinerary generation pipeline.
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
        sections.append(self._section("LOGISTICS", self._logistics_section(ctx)))
        sections.append(self._section("INTERESTS & ACTIVITIES", self._interests_section(ctx)))
        sections.append(self._section("SELECTED PROVIDERS", self._providers_section(ctx)))
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
            "logistics": {
                "destination": ctx.destination,
                "dates": ctx.travel_dates,
                "max_driving_hours": ctx.max_driving_hours,
                "flights": ctx.flight_details,
            },
            "interests": {
                "categories": ctx.interest_categories,
                "details": ctx.interest_details,
            },
            "providers": ctx.selected_providers,
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
    def _logistics_section(ctx: PlanningContext) -> str:
        lines = [
            f"- Destination: {ctx.destination or 'New Zealand'}",
            f"- Dates: {json.dumps(ctx.travel_dates, default=str) if ctx.travel_dates else 'flexible'}",
            f"- Max driving per day: {ctx.max_driving_hours or 'not specified'} hours",
            f"- Flights: {json.dumps(ctx.flight_details, default=str) if ctx.flight_details else 'not booked'}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _interests_section(ctx: PlanningContext) -> str:
        lines: list[str] = []
        for cat in ctx.interest_categories:
            activities = ctx.interest_details.get(cat, [])
            act_str = ", ".join(activities) if activities else "(no specifics)"
            lines.append(f"- {cat}: {act_str}")
        return "\n".join(lines) if lines else "- None specified"

    @staticmethod
    def _providers_section(ctx: PlanningContext) -> str:
        if not ctx.selected_providers:
            return "- Deferred all provider choices to Buddi"
        lines: list[str] = []
        for activity, provider in ctx.selected_providers.items():
            if isinstance(provider, dict):
                name = provider.get("name", "unknown")
                loc = provider.get("location", "")
                lines.append(f"- {activity}: {name} ({loc})" if loc else f"- {activity}: {name}")
            else:
                lines.append(f"- {activity}: {provider}")
        return "\n".join(lines)

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
        return (
            "## ITINERARY CONSTRAINTS\n"
            "- Optimise the route to minimise backtracking.\n"
            "- Spread activities geographically — don't cluster everything in one area.\n"
            "- Include flex/rest days proportional to trip length.\n"
            "- Balance hard and easy days based on the fitness profile.\n"
            "- Account for accessibility needs in every day's plan.\n"
            f"- Maximum driving per day: {ctx.max_driving_hours or 4} hours.\n"
            "- Include accommodation suggestions appropriate for the transport mode.\n"
            "- Note weather-sensitive activities and suggest optimal timing.\n"
        )
