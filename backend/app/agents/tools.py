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
    if ctx.group_type and not ctx.group_details.get("ages_raw"):
        missing.append("ages")
    if not ctx.accessibility_needs:
        missing.append("accessibility_needs")
    if not ctx.fitness_profile:
        missing.append("fitness_profile")
    if not ctx.budget:
        missing.append("budget")
    return missing


def logistics_missing(ctx: PlanningContext) -> list[str]:
    missing: list[str] = []
    if not ctx.travel_dates:
        missing.append("travel_dates")
    if not ctx.trip_duration:
        missing.append("trip_duration")
    if ctx.max_driving_hours is None:
        missing.append("max_driving_hours")
    return missing


def interest_categories_missing(ctx: PlanningContext) -> list[str]:
    if not ctx.interest_categories:
        return ["interest_categories"]
    return []


def island_preference_missing(ctx: PlanningContext) -> list[str]:
    if not ctx.island_preference:
        return ["island_preference"]
    return []


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

_GROUP_TYPE_ALIASES: dict[str, str] = {
    "solo": "solo",
    "flying solo": "solo",
    "just me": "solo",
    "alone": "solo",
    "couple": "couple",
    "with my partner": "couple",
    "partner": "couple",
    "two": "couple",
    "family": "family",
    "family trip": "family",
    "with family": "family",
    "friends": "friends",
    "friends trip": "friends",
    "with friends": "friends",
    "friend group": "friends",
}


@function_tool
async def set_group_type(
    ctx: RunContextWrapper[PlanningContext],
    group_type: str,
) -> str:
    """Set the travel group type. Must be one of: solo, couple, family, friends.
    Also accepts common phrases like 'Flying solo', 'With my partner', 'Family trip', 'Friends trip'."""
    normalized = _GROUP_TYPE_ALIASES.get(group_type.strip().lower(), group_type.strip().lower())
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


_ACCESSIBILITY_ALIASES: dict[str, str] = {
    "none": "none",
    "no accessibility needs": "none",
    "no special needs": "none",
    "no restrictions": "none",
    "all good": "none",
    "all good to go": "none",
    "stroller": "stroller",
    "travelling with stroller/pram": "stroller",
    "traveling with stroller/pram": "stroller",
    "stroller/pram": "stroller",
    "pram": "stroller",
    "pushchair": "stroller",
    "wheelchair": "wheelchair",
    "wheelchair or mobility aid": "wheelchair",
    "wheelchair accessible": "wheelchair",
    "mobility aid": "wheelchair",
    "wheelchair/stroller accessible only": "wheelchair",
    "full accessibility": "wheelchair",
    # legacy aliases kept for backward compatibility
    "minimal": "none",
    "prefer flat": "none",
    "prefer flat, paved paths": "none",
    "flat paths": "none",
    "paved paths": "none",
}

_FITNESS_ALIASES: dict[str, tuple[str, bool]] = {
    "light": ("light", False),
    "keep it relaxed": ("light", False),
    "keep it light": ("light", False),
    "relaxed": ("light", False),
    "easy": ("light", False),
    "gentle": ("light", False),
    "moderate": ("moderate", True),
    "active explorer": ("moderate", True),
    "up for a moderate challenge": ("moderate", True),
    "moderate challenge": ("moderate", True),
    "advanced": ("advanced", True),
    "endless energy": ("advanced", True),
    "bring on the big hikes": ("advanced", True),
    "hard hikes": ("advanced", True),
    "mixed": ("mixed", True),
    "a mix of everything": ("mixed", True),
    "mix": ("mixed", True),
    "some easy days, some big ones": ("mixed", True),
}


@function_tool
async def set_accessibility(
    ctx: RunContextWrapper[PlanningContext],
    level: str,
    notes: str = "",
) -> str:
    """Set accessibility requirements.
    Call this whenever the user states their accessibility preference, even if they say
    'No accessibility needs' or 'No special needs' — those map to level='none'.
    Accepted level values (also accepts full button labels):
      'none'        → no accessibility requirements ('No accessibility needs', 'No special needs')
      'stroller'    → travelling with stroller/pram — need pram-friendly paths and facilities
      'wheelchair'  → wheelchair or mobility aid — need fully accessible facilities throughout"""
    normalized = _ACCESSIBILITY_ALIASES.get(level.strip().lower(), level.strip().lower())
    ctx.context.accessibility_needs = {"level": normalized, "notes": notes}
    return _status("Accessibility set", travel_dna_missing(ctx.context))


@function_tool
async def set_fitness_profile(
    ctx: RunContextWrapper[PlanningContext],
    level: str,
    notes: str = "",
) -> str:
    """Set the group's fitness profile.
    Call this whenever the user states their fitness preference.
    Accepted level values (also accepts full button labels):
      'light'    → scenic drives, flat strolls, up to an hour of walking ('Keep it relaxed')
      'moderate' → a few hours on feet exploring towns, beaches, undulating paths ('Active explorer')
      'advanced' → highly physical days, steep climbs, full-day excursions ('Endless energy')
      'mixed'    → occasional push days balanced with easy recovery days ('A mix of everything')"""
    level_key, can_high_exertion = _FITNESS_ALIASES.get(level.strip().lower(), (level.strip().lower(), level.strip().lower() in ("moderate", "advanced", "mixed")))
    ctx.context.fitness_profile = {
        "general_level": level_key,
        "can_handle_high_exertion": can_high_exertion,
        "notes": notes,
    }
    return _status("Fitness profile set", travel_dna_missing(ctx.context))


_BUDGET_ALIASES: dict[str, str] = {
    "budget-friendly": "budget",
    "budget": "budget",
    "keep costs low": "budget",
    "cheap": "budget",
    "mid-range": "midrange",
    "midrange": "midrange",
    "happy to pay for great experiences": "midrange",
    "treat ourselves": "premium",
    "premium": "premium",
    "luxury": "premium",
    "splurge": "premium",
    "flexible": "flexible",
    "depends on the experience": "flexible",
}


@function_tool
async def set_budget(
    ctx: RunContextWrapper[PlanningContext],
    level: str,
    notes: str = "",
) -> str:
    """Set the travel budget comfort level.
    Call this whenever the user states their budget preference.
    Accepted level values (also accepts full button labels):
      'budget'   → keep costs low, free/cheap activities ('Budget-friendly')
      'midrange' → happy to pay for great experiences ('Mid-range')
      'premium'  → treat ourselves, no stress about cost ('Treat ourselves')
      'flexible' → depends on the experience ('Flexible')"""
    normalized = _BUDGET_ALIASES.get(level.strip().lower(), level.strip().lower())
    ctx.context.budget = {"level": normalized, "notes": notes}
    return _status("Budget set", travel_dna_missing(ctx.context))


# Public exports for direct-fill resolution in the orchestrator.
GROUP_TYPE_ALIASES: dict[str, str] = _GROUP_TYPE_ALIASES
ACCESSIBILITY_ALIASES: dict[str, str] = _ACCESSIBILITY_ALIASES
FITNESS_ALIASES: dict[str, tuple[str, bool]] = _FITNESS_ALIASES
BUDGET_ALIASES: dict[str, str] = _BUDGET_ALIASES


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
async def set_trip_duration(
    ctx: RunContextWrapper[PlanningContext],
    duration_type: str,
    days: int = 0,
    min_days: int = 0,
    max_days: int = 0,
    notes: str = "",
) -> str:
    """Record the trip duration preference.
    duration_type: 'fixed' (user has exact days), 'approximate' (rough range),
    or 'flexible' (open to suggestions based on activities).
    For 'fixed': provide days. For 'approximate': provide min_days and max_days."""
    duration: dict = {"type": duration_type.strip().lower()}
    if days:
        duration["days"] = days
    if min_days:
        duration["min_days"] = min_days
    if max_days:
        duration["max_days"] = max_days
    if notes:
        duration["notes"] = notes
    ctx.context.trip_duration = duration
    return _status("Trip duration recorded", logistics_missing(ctx.context))


@function_tool
async def set_max_driving_hours(
    ctx: RunContextWrapper[PlanningContext],
    hours: int,
) -> str:
    """Set the maximum comfortable driving hours per day."""
    ctx.context.max_driving_hours = hours
    return _status(f"Max driving set to {hours}h", logistics_missing(ctx.context))


# ═══════════════════════════════════════════════════════════════════════════
# Interest Categories tools
# ═══════════════════════════════════════════════════════════════════════════

from app.data.activity_taxonomy import CATEGORIES as _TAX_CATEGORIES
from app.data.nz_attractions import NZ_ATTRACTIONS as _NZ_ATTRACTIONS

CANONICAL_CATEGORIES = [
    {"label": c.label, "emoji": c.emoji, "description": c.description}
    for c in _TAX_CATEGORIES
]


@function_tool
async def set_interest_categories(
    ctx: RunContextWrapper[PlanningContext],
    categories: List[str],
) -> str:
    """Record the high-level interest categories selected by the user.

    The strict 9 TripAdvisor-aligned categories are:
      Attractions, Tours, Day Trips, Outdoor Activities, Concerts & Shows,
      Events, Classes & Workshops, Transportation, Traveler Resources.
    """
    ctx.context.interest_categories = categories
    return (
        f"Categories set: {', '.join(categories)}. "
        "All categories recorded! Hand off to the next agent now."
    )


# ═══════════════════════════════════════════════════════════════════════════
# Island Preference tools
# ═══════════════════════════════════════════════════════════════════════════

@function_tool
async def get_island_analysis(
    ctx: RunContextWrapper[PlanningContext],
) -> str:
    """Analyze which NZ islands best match the user's chosen categories.
    Call this to give the user an informed island recommendation based on
    where attractions in their chosen categories are concentrated."""
    chosen = ctx.context.interest_categories
    if not chosen:
        return json.dumps({"error": "No categories selected yet."})

    from app.data.activity_taxonomy import get_category_slug_for_label

    cat_slugs = set()
    for label in chosen:
        slug = get_category_slug_for_label(label)
        if slug:
            cat_slugs.add(slug)

    south_counts: dict[str, int] = {}
    north_counts: dict[str, int] = {}
    for att in _NZ_ATTRACTIONS:
        att_cat = att.get("category", "")
        if att_cat not in cat_slugs:
            continue
        island = att.get("metadata", {}).get("island", "")
        cat_label = next(
            (c.label for c in _TAX_CATEGORIES if c.slug == att_cat), att_cat
        )
        if island == "south":
            south_counts[cat_label] = south_counts.get(cat_label, 0) + 1
        elif island == "north":
            north_counts[cat_label] = north_counts.get(cat_label, 0) + 1

    south_strong = [c for c in chosen if south_counts.get(c, 0) > north_counts.get(c, 0)]
    north_strong = [c for c in chosen if north_counts.get(c, 0) > south_counts.get(c, 0)]
    balanced = [c for c in chosen if c not in south_strong and c not in north_strong]

    return json.dumps({
        "south_island_stronger": south_strong,
        "north_island_stronger": north_strong,
        "balanced_both_islands": balanced,
        "south_attraction_counts": south_counts,
        "north_attraction_counts": north_counts,
        "total_categories_selected": len(chosen),
    })


_ISLAND_ALIASES: dict[str, str] = {
    "south island": "south_only",
    "south island only": "south_only",
    "south only": "south_only",
    "south": "south_only",
    "north island": "north_only",
    "north island only": "north_only",
    "north only": "north_only",
    "north": "north_only",
    "both": "both",
    "both islands": "both",
    "help me decide": "both",
}


@function_tool
async def set_island_preference(
    ctx: RunContextWrapper[PlanningContext],
    preference: str,
    notes: str = "",
) -> str:
    """Record the user's island preference.
    preference: 'south_only', 'north_only', or 'both'."""
    normalized = _ISLAND_ALIASES.get(preference.strip().lower(), preference.strip().lower())
    islands_map = {
        "south_only": ["south"],
        "north_only": ["north"],
        "both": ["south", "north"],
    }
    ctx.context.island_preference = {
        "preference": normalized,
        "islands": islands_map.get(normalized, ["south", "north"]),
        "notes": notes,
    }
    return _status("Island preference set", island_preference_missing(ctx.context))


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
