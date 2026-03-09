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


def activity_location_remaining(ctx: PlanningContext) -> list[str]:
    return [a for a in _all_activities(ctx) if a not in ctx.activity_locations]


def location_summary_missing(ctx: PlanningContext) -> list[str]:
    missing: list[str] = []
    if not ctx.location_summary:
        missing.append("location_summary")
    if not ctx.days_per_location:
        missing.append("days_per_location")
    return missing


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
# These alias dicts allow the orchestrator to resolve controlled-choice button
# labels to their canonical values without needing an LLM call.
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

from app.data.activity_taxonomy import (
    CATEGORIES as _TAX_CATEGORIES,
    get_activities_for_category,
    get_activity,
    get_category_slug_for_label,
)
from app.data.nz_attractions import NZ_ATTRACTIONS as _NZ_ATTRACTIONS

CANONICAL_CATEGORIES = [c.label for c in _TAX_CATEGORIES]


def _build_activity_options() -> dict[str, list[str]]:
    """Derive ACTIVITY_OPTIONS from taxonomy + data.

    Only includes activities that have at least one real attraction.
    """
    activities_with_data: set[str] = {a["activity"] for a in _NZ_ATTRACTIONS if a.get("activity")}
    result: dict[str, list[str]] = {}
    for cat in _TAX_CATEGORIES:
        acts = get_activities_for_category(cat.slug)
        labels = [a.label for a in acts if a.slug in activities_with_data]
        if labels:
            result[cat.label] = labels
    return result


def _build_activity_location_map() -> dict[str, list[dict[str, str]]]:
    """Derive ACTIVITY_LOCATION_MAP from attraction data.

    Maps activity labels to their real locations/providers.
    """
    result: dict[str, list[dict[str, str]]] = {}
    for att in _NZ_ATTRACTIONS:
        act_slug = att.get("activity")
        if not act_slug:
            continue
        act = get_activity(act_slug)
        if not act:
            continue

        island = att.get("metadata", {}).get("island", "")
        route_fit = f"{island}-island" if island else "flexible"

        entry = {
            "location": att.get("location_name", ""),
            "name": att["name"],
            "region": att.get("region", ""),
            "route_fit": route_fit,
            "highlight": att.get("description", "")[:80],
        }
        result.setdefault(act.label, []).append(entry)

    for entries in result.values():
        entries.sort(key=lambda e: next(
            (a.get("uniqueness_score", 50) for a in _NZ_ATTRACTIONS if a["name"] == e["name"]),
            50,
        ), reverse=True)

    return result


ACTIVITY_OPTIONS: dict[str, list[str]] = _build_activity_options()
ACTIVITY_LOCATION_MAP: dict[str, list[dict[str, str]]] = _build_activity_location_map()


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
# Island Preference tools
# ═══════════════════════════════════════════════════════════════════════════

@function_tool
async def get_island_analysis(
    ctx: RunContextWrapper[PlanningContext],
) -> str:
    """Analyze which NZ islands the user's chosen activities are available on.
    Call this to give the user an informed island recommendation."""
    activities = _all_activities(ctx.context)
    south_only: list[str] = []
    north_only: list[str] = []
    both_islands: list[str] = []

    for activity in activities:
        locations = ACTIVITY_LOCATION_MAP.get(activity, [])
        islands: set[str] = set()
        for loc in locations:
            route_fit = loc.get("route_fit", "")
            if "south" in route_fit:
                islands.add("south")
            elif "north" in route_fit:
                islands.add("north")
        if "south" in islands and "north" in islands:
            both_islands.append(activity)
        elif "south" in islands:
            south_only.append(activity)
        elif "north" in islands:
            north_only.append(activity)
        else:
            both_islands.append(activity)

    return json.dumps({
        "south_island_only": south_only,
        "north_island_only": north_only,
        "available_on_both": both_islands,
        "total_activities": len(activities),
        "south_count": len(south_only) + len(both_islands),
        "north_count": len(north_only) + len(both_islands),
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
# Provider Selection tools
# ═══════════════════════════════════════════════════════════════════════════

def _build_provider_db() -> dict[str, list[dict]]:
    """Build a lookup from activity-label → list of real provider dicts.

    Uses the canonical taxonomy: each attraction's ``activity`` field maps
    directly to the activity label via the taxonomy registry.
    """
    providers: dict[str, list[dict]] = {}

    for att in _NZ_ATTRACTIONS:
        act_slug = att.get("activity")
        if not act_slug:
            continue
        act = get_activity(act_slug)
        if not act:
            continue

        logistics = att.get("logistics", {})
        cost_info = logistics.get("estimated_cost_nzd", {})
        adult_price = cost_info.get("adult", 0) if isinstance(cost_info, dict) else 0
        operator = att.get("metadata", {}).get("operator", "")

        provider_entry = {
            "name": att["name"],
            "location": att.get("location_name", ""),
            "region": att.get("region", ""),
            "price_nzd": adult_price,
            "price_notes": cost_info.get("notes", "") if isinstance(cost_info, dict) else "",
            "operator": operator,
            "booking_required": att.get("booking_required", False),
            "uniqueness_score": att.get("uniqueness_score", 50),
            "description": att.get("description", "")[:120],
            "weather_sensitivity": att.get("weather_sensitivity", "moderate"),
        }

        providers.setdefault(act.label, []).append(provider_entry)
        providers.setdefault(att["name"], []).append(provider_entry)

    return providers


_PROVIDER_DB: dict[str, list[dict]] | None = None


def _get_provider_db() -> dict[str, list[dict]]:
    global _PROVIDER_DB
    if _PROVIDER_DB is None:
        _PROVIDER_DB = _build_provider_db()
    return _PROVIDER_DB


@function_tool
async def get_real_providers(
    ctx: RunContextWrapper[PlanningContext],
    activity: str,
) -> str:
    """Get real provider options for an activity from the attractions database.
    Returns actual operators with real prices, locations, and details."""
    db = _get_provider_db()
    chosen_location = ctx.context.activity_locations.get(activity, "")

    candidates = db.get(activity, [])
    if not candidates:
        for key, providers in db.items():
            if activity.lower() in key.lower() or key.lower() in activity.lower():
                candidates = providers
                break

    if chosen_location:
        loc_lower = chosen_location.lower()
        local = [p for p in candidates if loc_lower in p.get("location", "").lower() or loc_lower in p.get("region", "").lower()]
        if local:
            candidates = local

    candidates.sort(key=lambda p: p.get("uniqueness_score", 50), reverse=True)
    return json.dumps(candidates[:5])


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


# ═══════════════════════════════════════════════════════════════════════════
# Activity-Location tools
# ═══════════════════════════════════════════════════════════════════════════





@function_tool
async def get_location_options(
    ctx: RunContextWrapper[PlanningContext],
    activity: str,
) -> str:
    """Get ranked location options where an activity can be done, so you can
    present them to the user for selection."""
    options = ACTIVITY_LOCATION_MAP.get(activity)
    if options:
        islands = ctx.context.island_preference.get("islands", [])
        if islands and set(islands) != {"south", "north"}:
            filtered = [
                loc for loc in options
                if any(island in loc.get("route_fit", "") for island in islands)
            ]
            if filtered:
                options = filtered
        return json.dumps(options)
    return json.dumps([{
        "location": "Unknown",
        "name": activity,
        "region": "varies",
        "route_fit": "flexible",
        "highlight": "Ask the user where they'd prefer to do this",
    }])


@function_tool
async def set_activity_location(
    ctx: RunContextWrapper[PlanningContext],
    activity: str,
    location: str,
) -> str:
    """Record which location the user chose for a specific activity."""
    ctx.context.activity_locations[activity] = location
    remaining = activity_location_remaining(ctx.context)
    return _status(f"'{activity}' → {location}", remaining)


# ═══════════════════════════════════════════════════════════════════════════
# Location Summary tools
# ═══════════════════════════════════════════════════════════════════════════

SIGHTSEEING_BY_LOCATION: dict[str, list[str]] = {
    "Queenstown": ["Skyline Gondola & Luge", "Glenorchy scenic drive", "Fergburger", "Lake Wakatipu waterfront walk"],
    "Wanaka": ["That Wanaka Tree", "Puzzling World", "Lavender Farm", "Cinema Paradiso"],
    "Rotorua": ["Kuirau Park geothermal", "Redwoods Treewalk", "Government Gardens", "Eat Street dining"],
    "Taupo": ["Aratiatia Rapids", "Huka Falls walk", "Craters of the Moon", "Great Lake Taupo lookouts"],
    "Tongariro": ["Meads Wall (LOTR)", "Taranaki Falls loop", "Chateau Tongariro tea"],
    "Kaikoura": ["Seal Colony walk (free)", "Kaikoura Peninsula Walkway", "Seafood at Nin's Bin crayfish"],
    "Franz Josef": ["Roberts Point Track", "Glacier Valley walk (free)", "West Coast Wildlife Centre"],
    "Abel Tasman": ["Cleopatra's Pool", "Split Apple Rock", "Kaiteriteri beach"],
    "Dunedin": ["Baldwin Street (steepest)", "Larnach Castle", "Tunnel Beach", "Cadbury World"],
    "Milford Sound": ["The Chasm walk", "Mirror Lakes", "Key Summit Track"],
    "Waiheke Island": ["Onetangi Beach", "Cable Bay walkway", "Batch Winery sunset"],
    "Waitomo": ["Mangapohue Natural Bridge", "Marokopa Falls", "Piripiri Cave"],
    "Matamata": ["Hobbiton", "Wairere Falls (NI's tallest)", "Firth Tower Museum"],
    "Hahei": ["Hot Water Beach (tide dependent)", "Stingray Bay snorkelling", "Cathedral Cove"],
    "Lake Tekapo": ["Church of the Good Shepherd", "Mt John walkway (free)", "Lupins (Nov-Dec)"],
    "Aoraki/Mt Cook": ["Hooker Valley Track", "Tasman Glacier viewpoint", "Sir Edmund Hillary Centre"],
    "Punakaiki": ["Pancake Rocks + Blowholes", "Truman Track hidden beach"],
    "Taranaki": ["Pouakai Tarn", "Three Sisters", "New Plymouth coastal walkway"],
    "Putaruru": ["Blue Spring / Te Waihou Walkway"],
    "Whitianga": ["The Lost Spring", "Flaxmill Bay", "Mercury Bay"],
    "Marlborough": ["Wine trail by bike", "Kenepuru Sound drive"],
    "Canterbury": ["International Antarctic Centre", "Christchurch Botanic Gardens", "Port Hills walk"],
    "Akaroa": ["Hector's dolphin swim", "French colonial architecture walk", "Giant's House"],
}


@function_tool
async def build_location_summary(
    ctx: RunContextWrapper[PlanningContext],
) -> str:
    """Build a per-location summary grouping all chosen activities and
    recommending sightseeing and days per location. Call this once all
    activity locations are set."""
    activity_locs = ctx.context.activity_locations
    if not activity_locs:
        return "No activity locations set yet. Complete activity-location selection first."

    summary: dict[str, dict] = {}
    for activity, location in activity_locs.items():
        if location not in summary:
            summary[location] = {"activities": [], "sightseeing": [], "recommended_days": 0}
        summary[location]["activities"].append(activity)

    for location, data in summary.items():
        data["sightseeing"] = SIGHTSEEING_BY_LOCATION.get(location, [])
        act_count = len(data["activities"])
        data["recommended_days"] = max(1, (act_count + 1) // 2) + (1 if data["sightseeing"] else 0)

    ctx.context.location_summary = summary
    ctx.context.days_per_location = {
        loc: data["recommended_days"] for loc, data in summary.items()
    }
    total_days = sum(d["recommended_days"] for d in summary.values())
    return json.dumps({
        "summary": summary,
        "total_activity_days": total_days,
    })


@function_tool
async def adjust_location_days(
    ctx: RunContextWrapper[PlanningContext],
    location: str,
    days: int,
) -> str:
    """Adjust the number of days allocated to a specific location."""
    if location not in ctx.context.days_per_location:
        return f"Location '{location}' not in the plan. Available: {list(ctx.context.days_per_location.keys())}"
    ctx.context.days_per_location[location] = days
    if location in ctx.context.location_summary:
        ctx.context.location_summary[location]["recommended_days"] = days
    total = sum(ctx.context.days_per_location.values())
    return f"Days for {location} set to {days}. Total trip days: {total}."


@function_tool
async def confirm_location_plan(
    ctx: RunContextWrapper[PlanningContext],
) -> str:
    """Confirm the location plan. Call when the user approves the summary."""
    missing = location_summary_missing(ctx.context)
    return _status("Location plan confirmed", missing)
