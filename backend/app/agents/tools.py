"""Function tools for every planning agent.

Each tool updates ``PlanningContext`` in-place and returns a status string
that tells the agent what is still missing (so it knows whether to ask
another question or hand off to the next agent).
"""
from __future__ import annotations

import json
from typing import List

from agents import function_tool, RunContextWrapper

from app.agents.context import PlanningContext


# ═══════════════════════════════════════════════════════════════════════════
# Status helpers (shared by tools and orchestrator)
# ═══════════════════════════════════════════════════════════════════════════

def travel_dna_missing(ctx: PlanningContext) -> list[str]:
    missing: list[str] = []
    if not ctx.group_type:
        missing.append("group_type")
    elif ctx.group_type in ("family", "friends"):
        if not ctx.group_details.get("count"):
            missing.append("group_count")
        elif not ctx.group_details.get("ages_raw"):
            missing.append("ages")
    if not ctx.accessibility_needs:
        missing.append("accessibility_needs")
    if not ctx.fitness_profile:
        missing.append("fitness_profile")
    return missing


def logistics_missing(ctx: PlanningContext) -> list[str]:
    missing: list[str] = []
    if not ctx.travel_dates:
        missing.append("travel_dates")
    if ctx.max_driving_hours is None:
        missing.append("max_driving_hours")
    if not ctx.flight_details:
        missing.append("flight_details")
    return missing


def interest_categories_missing(ctx: PlanningContext) -> list[str]:
    if not ctx.interest_categories:
        return ["interest_categories"]
    return []


def interest_deep_dive_remaining(ctx: PlanningContext) -> list[str]:
    return [
        cat for cat in ctx.interest_categories
        if cat not in ctx.interest_details or not ctx.interest_details[cat]
    ]


def _all_activities(ctx: PlanningContext) -> list[str]:
    activities: list[str] = []
    for cat in ctx.interest_categories:
        for act in ctx.interest_details.get(cat, []):
            if act not in activities:
                activities.append(act)
    return activities


def provider_selection_remaining(ctx: PlanningContext) -> list[str]:
    return [a for a in _all_activities(ctx) if a not in ctx.selected_providers]


def transport_route_missing(ctx: PlanningContext) -> list[str]:
    missing: list[str] = []
    if not ctx.transport_plan:
        missing.append("transport_mode")
    if not ctx.route_direction:
        missing.append("route_direction")
    return missing


def _status(label: str, remaining: list[str]) -> str:
    if remaining:
        return f"{label} — still need: {', '.join(remaining)}. Ask the next question."
    return f"{label} — all data collected! Hand off to the next agent now."


# ═══════════════════════════════════════════════════════════════════════════
# Greeting tools
# ═══════════════════════════════════════════════════════════════════════════

@function_tool
async def get_tell_me_more_info(ctx: RunContextWrapper[PlanningContext]) -> str:
    """Return detailed information about Journey Buddi. Call this when the
    user says 'Tell me more' or wants to know what the app does."""
    from app.services.tell_me_more_options import ACTIVE_TELL_ME_MORE
    return ACTIVE_TELL_ME_MORE


# ═══════════════════════════════════════════════════════════════════════════
# Travel DNA tools
# ═══════════════════════════════════════════════════════════════════════════

@function_tool
async def set_group_type(
    ctx: RunContextWrapper[PlanningContext],
    group_type: str,
) -> str:
    """Set the travel group type. Must be one of: solo, couple, family, friends."""
    normalized = group_type.strip().lower()
    valid = {"solo", "couple", "family", "friends"}
    if normalized not in valid:
        return f"Invalid group type '{group_type}'. Must be one of: {', '.join(sorted(valid))}"
    ctx.context.group_type = normalized
    if normalized == "solo":
        ctx.context.group_details = {"count": 1}
    elif normalized == "couple":
        ctx.context.group_details = {"count": 2}
    return _status("Group type set to " + normalized, travel_dna_missing(ctx.context))


@function_tool
async def set_group_count(
    ctx: RunContextWrapper[PlanningContext],
    count: int,
) -> str:
    """Set how many people are in the travel group (for family/friends)."""
    if not ctx.context.group_details:
        ctx.context.group_details = {}
    ctx.context.group_details["count"] = count
    return _status(f"Group count set to {count}", travel_dna_missing(ctx.context))


@function_tool
async def set_group_ages(
    ctx: RunContextWrapper[PlanningContext],
    ages_description: str,
) -> str:
    """Record the ages of all travelers as described by the user."""
    if not ctx.context.group_details:
        ctx.context.group_details = {}
    ctx.context.group_details["ages_raw"] = ages_description
    return _status("Ages recorded", travel_dna_missing(ctx.context))


@function_tool
async def set_accessibility(
    ctx: RunContextWrapper[PlanningContext],
    level: str,
    notes: str = "",
) -> str:
    """Set accessibility requirements. Level should be: none, minimal, or wheelchair."""
    ctx.context.accessibility_needs = {"level": level.strip().lower(), "notes": notes}
    return _status("Accessibility set", travel_dna_missing(ctx.context))


@function_tool
async def set_fitness_profile(
    ctx: RunContextWrapper[PlanningContext],
    general_level: str,
    can_handle_hard_hikes: bool,
    notes: str = "",
) -> str:
    """Set the group's fitness profile.
    general_level: light, moderate, advanced, or mixed.
    can_handle_hard_hikes: whether the group can handle 1-2 hard hikes.
    notes: any extra nuance from the user."""
    ctx.context.fitness_profile = {
        "general_level": general_level.strip().lower(),
        "can_handle_hard_hikes": can_handle_hard_hikes,
        "notes": notes,
    }
    return _status("Fitness profile set", travel_dna_missing(ctx.context))


# ═══════════════════════════════════════════════════════════════════════════
# Logistics tools
# ═══════════════════════════════════════════════════════════════════════════

@function_tool
async def set_travel_dates(
    ctx: RunContextWrapper[PlanningContext],
    season: str = "",
    start_date: str = "",
    end_date: str = "",
    duration_days: int = 0,
    flexibility: str = "",
    notes: str = "",
) -> str:
    """Record the user's travel dates or seasonal preference.
    Provide whichever fields the user mentioned."""
    dates: dict = {}
    if season:
        dates["season"] = season
    if start_date:
        dates["start_date"] = start_date
    if end_date:
        dates["end_date"] = end_date
    if duration_days:
        dates["duration_days"] = duration_days
    if flexibility:
        dates["flexibility"] = flexibility
    if notes:
        dates["notes"] = notes
    ctx.context.travel_dates = dates
    if not ctx.context.destination:
        ctx.context.destination = "New Zealand"
    return _status("Travel dates recorded", logistics_missing(ctx.context))


@function_tool
async def set_max_driving_hours(
    ctx: RunContextWrapper[PlanningContext],
    hours: int,
) -> str:
    """Set the maximum comfortable driving hours per day."""
    ctx.context.max_driving_hours = hours
    return _status(f"Max driving set to {hours}h", logistics_missing(ctx.context))


@function_tool
async def set_flight_details(
    ctx: RunContextWrapper[PlanningContext],
    status: str,
    arrival_city: str = "",
    departure_city: str = "",
    arrival_date: str = "",
    departure_date: str = "",
    notes: str = "",
) -> str:
    """Record flight booking status and details.
    status: booked, not_yet, or need_help."""
    details: dict = {"status": status}
    if arrival_city:
        details["arrival_city"] = arrival_city
    if departure_city:
        details["departure_city"] = departure_city
    if arrival_date:
        details["arrival_date"] = arrival_date
    if departure_date:
        details["departure_date"] = departure_date
    if notes:
        details["notes"] = notes
    ctx.context.flight_details = details
    return _status("Flight details recorded", logistics_missing(ctx.context))


# ═══════════════════════════════════════════════════════════════════════════
# Interest Categories tools
# ═══════════════════════════════════════════════════════════════════════════

CANONICAL_CATEGORIES = [
    "Mountains & Hiking", "Ocean & Marine Life", "Beaches & Coast",
    "Volcanoes & Geothermal", "Nature & Wildlife", "Food & Wine",
    "Adrenaline & Thrills", "Culture & History", "Photography & Scenery",
    "Stargazing & Dark Skies", "Water Sports", "Hot Springs & Relaxation",
]


@function_tool
async def set_interest_categories(
    ctx: RunContextWrapper[PlanningContext],
    categories: List[str],
) -> str:
    """Record the high-level interest categories selected by the user."""
    ctx.context.interest_categories = categories
    return (
        f"Categories set: {', '.join(categories)}. "
        "All categories recorded! Hand off to the Interest Deep Dive agent."
    )


# ═══════════════════════════════════════════════════════════════════════════
# Interest Deep Dive tools
# ═══════════════════════════════════════════════════════════════════════════

ACTIVITY_OPTIONS: dict[str, list[str]] = {
    "Mountains & Hiking": [
        "Day hikes to summits", "Multi-day treks", "Coastal walks",
        "Forest walks", "Glacier hikes", "Ridge walks",
    ],
    "Ocean & Marine Life": [
        "Whale watching", "Swim with dolphins", "Snorkeling",
        "Scuba diving", "Kayaking", "Sailing", "Surfing",
    ],
    "Beaches & Coast": [
        "Beach walks", "Coastal hikes", "Rock pooling",
        "Beach camping", "Hidden coves exploration",
    ],
    "Volcanoes & Geothermal": [
        "Hot springs", "Mud pools", "Geysers",
        "Volcanic crater walks", "Geothermal parks",
    ],
    "Nature & Wildlife": [
        "Whale watching", "Swim with dolphins", "Penguin colonies",
        "Seal watching", "Birdwatching", "Glowworm caves", "Kiwi spotting",
    ],
    "Food & Wine": [
        "Vineyard tours", "Wine tasting", "Cooking classes",
        "Food markets", "Craft beer tours", "Farm-to-table dining",
    ],
    "Adrenaline & Thrills": [
        "Skydiving", "Bungy jumping", "Jet boating",
        "White water rafting", "Zip-lining", "Canyoning", "Paragliding",
    ],
    "Culture & History": [
        "Māori cultural experiences", "Museums", "Historical sites",
        "Art galleries", "Heritage trails",
    ],
    "Photography & Scenery": [
        "Landscape photography", "Sunrise / sunset spots",
        "Aerial photography", "Wildlife photography",
    ],
    "Stargazing & Dark Skies": [
        "Stargazing tours", "Dark sky reserves",
        "Astrophotography", "Aurora viewing",
    ],
    "Water Sports": [
        "Kayaking", "Surfing", "Stand-up paddleboarding",
        "Jet skiing", "Fishing", "Sailing",
    ],
    "Hot Springs & Relaxation": [
        "Natural hot springs", "Spa experiences",
        "Thermal pools", "Wellness retreats",
    ],
}


@function_tool
async def get_activity_options(
    ctx: RunContextWrapper[PlanningContext],
    category: str,
) -> str:
    """Get the available activity types for an interest category so you can
    present them to the user as choices."""
    options = ACTIVITY_OPTIONS.get(category)
    if options:
        return json.dumps(options)
    return f"No predefined activities for '{category}'. Ask the user as a free-text question."


@function_tool
async def set_interest_activities(
    ctx: RunContextWrapper[PlanningContext],
    category: str,
    activities: List[str],
) -> str:
    """Record the specific activity types the user chose for a category."""
    ctx.context.interest_details[category] = activities
    remaining = interest_deep_dive_remaining(ctx.context)
    return _status(f"Activities for '{category}' recorded", remaining)


# ═══════════════════════════════════════════════════════════════════════════
# Provider Selection tools
# ═══════════════════════════════════════════════════════════════════════════

@function_tool
async def set_provider(
    ctx: RunContextWrapper[PlanningContext],
    activity: str,
    provider_name: str,
    location: str = "",
    notes: str = "",
) -> str:
    """Record the provider/operator selected for an activity.
    Use provider_name='buddi_pick' when the user defers the choice."""
    ctx.context.selected_providers[activity] = {
        "name": provider_name,
        "location": location,
        "notes": notes,
    }
    remaining = provider_selection_remaining(ctx.context)
    return _status(f"Provider for '{activity}' set to {provider_name}", remaining)


# ═══════════════════════════════════════════════════════════════════════════
# Transport & Route tools
# ═══════════════════════════════════════════════════════════════════════════

@function_tool
async def set_transport_mode(
    ctx: RunContextWrapper[PlanningContext],
    mode: str,
    details: str = "",
) -> str:
    """Set the transport mode. Should be: campervan, car, mix, or public."""
    ctx.context.transport_plan = {"mode": mode.strip().lower(), "details": details}
    return _status("Transport mode set", transport_route_missing(ctx.context))


@function_tool
async def set_route_direction(
    ctx: RunContextWrapper[PlanningContext],
    direction: str,
) -> str:
    """Set the route direction. Should be: clockwise, counter-clockwise, or custom."""
    ctx.context.route_direction = direction.strip().lower()
    return _status("Route direction set", transport_route_missing(ctx.context))
