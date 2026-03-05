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


def activity_location_remaining(ctx: PlanningContext) -> list[str]:
    return [a for a in _all_activities(ctx) if a not in ctx.activity_locations]


def location_summary_missing(ctx: PlanningContext) -> list[str]:
    missing: list[str] = []
    if not ctx.location_summary:
        missing.append("location_summary")
    if not ctx.days_per_location:
        missing.append("days_per_location")
    return missing


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

def _build_provider_db() -> dict[str, list[dict]]:
    """Build a lookup of activity → real providers from the attractions data."""
    from app.data.nz_attractions import NZ_ATTRACTIONS

    providers: dict[str, list[dict]] = {}

    activity_type_map = {
        "bungy": "Bungy jumping",
        "adrenaline": None,
        "adventure": None,
        "skydive": "Skydiving",
        "jet-boat": "Jet boating",
        "zipline": "Zip-lining",
        "rafting": "White water rafting",
        "canyoning": "Canyoning",
        "paragliding": "Paragliding",
        "horse-riding": "Horse riding",
        "balloon": "Hot air balloon",
        "hiking": "Day hikes to summits",
        "kayaking": "Kayaking",
        "cruise": "Cruises",
        "wildlife": "Wildlife watching",
        "wine": "Vineyard tours",
        "spa": "Spa experiences",
        "geothermal": "Geothermal parks",
        "cultural": "Cultural experiences",
        "cave": "Cave tours",
        "stargazing": "Stargazing tours",
    }

    for att in NZ_ATTRACTIONS:
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

        for att_type in att.get("types", []):
            activity_name = activity_type_map.get(att_type)
            if activity_name:
                providers.setdefault(activity_name, []).append(provider_entry)

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

ACTIVITY_LOCATION_MAP: dict[str, list[dict[str, str]]] = {
    "Bungy jumping": [
        {"location": "Queenstown", "name": "Nevis Bungy (134m)", "region": "otago", "route_fit": "south-island", "highlight": "NZ's highest — 8.5 sec freefall"},
        {"location": "Queenstown", "name": "Kawarau Bridge Bungy (43m)", "region": "otago", "route_fit": "south-island", "highlight": "Birthplace of commercial bungy"},
        {"location": "Taupo", "name": "Taupo Cliff Bungy (47m)", "region": "waikato", "route_fit": "north-island", "highlight": "River water-touch option"},
    ],
    "Skydiving": [
        {"location": "Queenstown", "name": "NZONE Skydive", "region": "otago", "route_fit": "south-island", "highlight": "Remarkables + Lake Wakatipu views"},
        {"location": "Wanaka", "name": "Skydive Wanaka", "region": "otago", "route_fit": "south-island", "highlight": "Alpine lake panorama, less crowded"},
    ],
    "Jet boating": [
        {"location": "Queenstown", "name": "Shotover Jet", "region": "otago", "route_fit": "south-island", "highlight": "Narrow canyon at 85 km/h"},
        {"location": "Taupo", "name": "Huka Falls Jet", "region": "waikato", "route_fit": "north-island", "highlight": "Near NZ's most famous waterfall"},
    ],
    "Zip-lining": [
        {"location": "Rotorua", "name": "Rotorua Canopy Tours", "region": "rotorua", "route_fit": "north-island", "highlight": "Best in NZ — ancient native bush, eco-focused"},
        {"location": "Queenstown", "name": "Ziptrek Ecotours", "region": "otago", "route_fit": "south-island", "highlight": "Treehouse platforms, Skyline hill views"},
        {"location": "Waiheke Island", "name": "EcoZip Adventures", "region": "auckland", "route_fit": "north-island", "highlight": "Dual ziplines over vineyards + forest walk"},
    ],
    "Canyoning": [
        {"location": "Wanaka", "name": "Deep Canyon", "region": "otago", "route_fit": "south-island", "highlight": "Waterfall rappelling + cliff jumps"},
    ],
    "White water rafting": [
        {"location": "Rotorua", "name": "Kaituna Cascades", "region": "rotorua", "route_fit": "north-island", "highlight": "7m Tutea Falls — highest commercially rafted waterfall"},
    ],
    "Paragliding": [
        {"location": "Queenstown", "name": "Coronet Peak Tandems", "region": "otago", "route_fit": "south-island", "highlight": "Remarkables views, premier NZ site"},
        {"location": "Wanaka", "name": "Wanaka Paragliding", "region": "otago", "route_fit": "south-island", "highlight": "Backup for Queenstown weather"},
    ],
    "Day hikes to summits": [
        {"location": "Wanaka", "name": "Roys Peak Track", "region": "otago", "route_fit": "south-island", "highlight": "Famous Insta ridgeline, 1200m gain"},
        {"location": "Tongariro", "name": "Tongariro Alpine Crossing", "region": "tongariro", "route_fit": "north-island", "highlight": "NZ's most famous day hike"},
        {"location": "Tongariro", "name": "Tama Lakes Track", "region": "tongariro", "route_fit": "north-island", "highlight": "Dramatic volcanic lakes, less crowded"},
    ],
    "Glacier hikes": [
        {"location": "Franz Josef", "name": "Franz Josef Heli-Hike", "region": "west-coast", "route_fit": "south-island", "highlight": "Helicopter onto glacier, blue ice caves"},
    ],
    "Coastal walks": [
        {"location": "Abel Tasman", "name": "Abel Tasman Coast Track", "region": "nelson-tasman", "route_fit": "south-island", "highlight": "Golden beaches, turquoise water"},
        {"location": "Hahei", "name": "Cathedral Cove Walk", "region": "coromandel", "route_fit": "north-island", "highlight": "Iconic rock arch, Narnia filming site"},
    ],
    "Whale watching": [
        {"location": "Kaikoura", "name": "Whale Watch Kaikoura", "region": "marlborough", "route_fit": "south-island", "highlight": "95% sighting success, sperm whales"},
    ],
    "Swim with dolphins": [
        {"location": "Akaroa", "name": "Black Cat Cruises", "region": "canterbury", "route_fit": "south-island", "highlight": "World's smallest dolphin — Hector's"},
    ],
    "Kayaking": [
        {"location": "Abel Tasman", "name": "Abel Tasman Kayaks", "region": "nelson-tasman", "route_fit": "south-island", "highlight": "Seal colony, golden coast"},
        {"location": "Milford Sound", "name": "Rosco's Milford Kayaks", "region": "southland-fiordland", "route_fit": "south-island", "highlight": "Fiord kayaking beneath waterfalls"},
    ],
    "Vineyard tours": [
        {"location": "Waiheke Island", "name": "Wine Mile Self-Guided", "region": "auckland", "route_fit": "north-island", "highlight": "4 world-class wineries walkable"},
        {"location": "Marlborough", "name": "Jade Tours", "region": "marlborough", "route_fit": "south-island", "highlight": "World-famous Sauvignon Blanc region"},
        {"location": "Queenstown", "name": "Gibbston Valley Bike & Wine", "region": "otago", "route_fit": "south-island", "highlight": "Pinot Noir + mountain scenery + bungy bridge"},
    ],
    "Wine tasting": [
        {"location": "Waiheke Island", "name": "Wine Mile Self-Guided", "region": "auckland", "route_fit": "north-island", "highlight": "4 world-class wineries walkable"},
        {"location": "Marlborough", "name": "Jade Tours", "region": "marlborough", "route_fit": "south-island", "highlight": "World-famous Sauvignon Blanc region"},
        {"location": "Queenstown", "name": "Gibbston Valley Bike & Wine", "region": "otago", "route_fit": "south-island", "highlight": "Pinot Noir + mountain scenery + bungy bridge"},
    ],
    "Natural hot springs": [
        {"location": "Rotorua", "name": "Polynesian Spa", "region": "rotorua", "route_fit": "north-island", "highlight": "28 pools, lakeside, acidic + alkaline"},
        {"location": "Queenstown", "name": "Onsen Hot Pools", "region": "otago", "route_fit": "south-island", "highlight": "Private cedar tubs, river + mountain views"},
        {"location": "Lake Tekapo", "name": "Tekapo Springs", "region": "canterbury", "route_fit": "south-island", "highlight": "Hot pools + stargazing combo"},
        {"location": "Taupo", "name": "Otumuheke Stream", "region": "waikato", "route_fit": "north-island", "highlight": "FREE natural thermal river"},
    ],
    "Thermal pools": [
        {"location": "Rotorua", "name": "Polynesian Spa", "region": "rotorua", "route_fit": "north-island", "highlight": "28 pools, lakeside, acidic + alkaline"},
        {"location": "Queenstown", "name": "Onsen Hot Pools", "region": "otago", "route_fit": "south-island", "highlight": "Private cedar tubs, river + mountain views"},
        {"location": "Taupo", "name": "Wairakei Terraces", "region": "waikato", "route_fit": "north-island", "highlight": "Blue silica terraces + thermal pools"},
    ],
    "Spa experiences": [
        {"location": "Queenstown", "name": "Onsen Hot Pools", "region": "otago", "route_fit": "south-island", "highlight": "Luxury private cedar hot tubs"},
        {"location": "Whitianga", "name": "The Lost Spring", "region": "coromandel", "route_fit": "north-island", "highlight": "Tropical landscaping, cocktails in-pool"},
    ],
    "Glowworm caves": [
        {"location": "Waitomo", "name": "Waitomo Glowworm Caves", "region": "waikato", "route_fit": "north-island", "highlight": "Millions of glowworms, silent boat ride"},
        {"location": "Waitomo", "name": "Spellbound Caves", "region": "waikato", "route_fit": "north-island", "highlight": "Intimate tour, fewer crowds"},
    ],
    "Hot springs": [
        {"location": "Rotorua", "name": "Polynesian Spa", "region": "rotorua", "route_fit": "north-island", "highlight": "NZ's flagship spa, 28 pools"},
        {"location": "Queenstown", "name": "Onsen Hot Pools", "region": "otago", "route_fit": "south-island", "highlight": "Private cedar tubs"},
        {"location": "Taupo", "name": "Otumuheke Stream", "region": "waikato", "route_fit": "north-island", "highlight": "FREE natural thermal river"},
    ],
    "Geysers": [
        {"location": "Rotorua", "name": "Te Puia (Pohutu Geyser)", "region": "rotorua", "route_fit": "north-island", "highlight": "NZ's most active geyser + Maori culture"},
    ],
    "Geothermal parks": [
        {"location": "Rotorua", "name": "Wai-O-Tapu", "region": "rotorua", "route_fit": "north-island", "highlight": "Most colorful geothermal area in NZ"},
        {"location": "Taupo", "name": "Craters of the Moon", "region": "waikato", "route_fit": "north-island", "highlight": "Steaming craters on supervolcano"},
    ],
    "Mud pools": [
        {"location": "Rotorua", "name": "Hell's Gate Mud Bath", "region": "rotorua", "route_fit": "north-island", "highlight": "Only geothermal mud bath in NZ"},
        {"location": "Rotorua", "name": "Wai-O-Tapu", "region": "rotorua", "route_fit": "north-island", "highlight": "Massive boiling mud bubbles (free roadside)"},
    ],
    "Penguin colonies": [
        {"location": "Dunedin", "name": "Otago Peninsula Wildlife", "region": "otago", "route_fit": "south-island", "highlight": "Yellow-eyed + blue penguins, wild beach"},
    ],
    "Seal watching": [
        {"location": "Kaikoura", "name": "Kaikoura Seal Colony Walk", "region": "marlborough", "route_fit": "south-island", "highlight": "Free, NZ fur seals on rocks"},
    ],
    "Māori cultural experiences": [
        {"location": "Rotorua", "name": "Te Puia", "region": "rotorua", "route_fit": "north-island", "highlight": "Geyser + carving school + kiwi house + haka"},
    ],
    "Stargazing tours": [
        {"location": "Lake Tekapo", "name": "Mt John Observatory", "region": "canterbury", "route_fit": "south-island", "highlight": "World's largest dark sky reserve"},
    ],
    "Landscape photography": [
        {"location": "Wanaka", "name": "Roys Peak", "region": "otago", "route_fit": "south-island", "highlight": "Famous ridgeline photo"},
        {"location": "Aoraki/Mt Cook", "name": "Hooker Valley Track", "region": "canterbury", "route_fit": "south-island", "highlight": "Swing bridges + icebergs + NZ's highest peak"},
        {"location": "Fox Glacier", "name": "Lake Matheson", "region": "west-coast", "route_fit": "south-island", "highlight": "Mirror reflections of Mt Cook + Tasman"},
    ],
    "Sunrise / sunset spots": [
        {"location": "Taranaki", "name": "Pouakai Tarn", "region": "taranaki", "route_fit": "north-island", "highlight": "Famous Mt Taranaki reflection"},
        {"location": "Lake Tekapo", "name": "Church of the Good Shepherd", "region": "canterbury", "route_fit": "south-island", "highlight": "Milky Way over iconic church"},
    ],
}


@function_tool
async def get_location_options(
    ctx: RunContextWrapper[PlanningContext],
    activity: str,
) -> str:
    """Get ranked location options where an activity can be done, so you can
    present them to the user for selection."""
    options = ACTIVITY_LOCATION_MAP.get(activity)
    if options:
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
