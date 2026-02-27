"""Generate day-by-day itineraries from planning state and selected attractions."""
from __future__ import annotations

import math
from typing import Optional

import structlog

log = structlog.get_logger()

# South Island route order (clockwise from Christchurch)
ROUTE_ORDER = [
    "Christchurch",
    "Kaikoura",
    "Hanmer Springs",
    "Nelson",
    "Abel Tasman",
    "West Coast",
    "Punakaiki",
    "Franz Josef",
    "Wanaka",
    "Queenstown",
    "Milford Sound",
    "Te Anau",
    "Dunedin",
]

# Keywords to map attraction locations to route areas (region string matching)
LOCATION_KEYWORDS = {
    "Christchurch": ["christchurch", "lyttelton", "akaroa"],
    "Kaikoura": ["kaikoura"],
    "Hanmer Springs": ["hanmer", "hanmer springs"],
    "Nelson": ["nelson", "motueka"],
    "Abel Tasman": ["abel tasman", "kaiteriteri", "marahau"],
    "West Coast": ["west coast", "greymouth", "hokitika"],
    "Punakaiki": ["punakaiki", "pancake rocks"],
    "Franz Josef": ["franz josef", "franz josef glacier", "fox glacier", "glacier"],
    "Wanaka": ["wanaka", "cardrona", "treble cone"],
    "Queenstown": ["queenstown", "arrowtown", "glenorchy"],
    "Milford Sound": ["milford", "milford sound", "fiordland"],
    "Te Anau": ["te anau", "manapouri"],
    "Dunedin": ["dunedin", "otago peninsula", "oamaru"],
}


def _get_attr(attraction: dict, key: str, default=None):
    """Get attr from dict or object."""
    if isinstance(attraction, dict):
        return attraction.get(key, default)
    return getattr(attraction, key, default)


def _get_attraction_location(attraction: dict) -> str:
    """Extract location from attraction (region, location_name, or name)."""
    for key in ("region", "location_name", "location"):
        val = _get_attr(attraction, key)
        if val and isinstance(val, str):
            return val.strip()
    return ""


def _match_to_route_area(location: str) -> str:
    """Map a location string to the nearest route area."""
    loc_lower = location.lower() if location else ""
    for area, keywords in LOCATION_KEYWORDS.items():
        for kw in keywords:
            if kw in loc_lower:
                return area
    return "Christchurch"  # default


def _cluster_attractions(attractions: list) -> dict[str, list]:
    """Group attractions by route area."""
    clusters: dict[str, list] = {}
    for att in attractions:
        loc = _get_attraction_location(att)
        area = _match_to_route_area(loc)
        clusters.setdefault(area, []).append(att)
    return clusters


def _order_areas_by_route(areas: set[str]) -> list[str]:
    """Order area names by route (Christchurch → south island clockwise)."""
    ordered = []
    for area in ROUTE_ORDER:
        if area in areas:
            ordered.append(area)
    # Any unmapped areas go at end
    for area in sorted(areas):
        if area not in ordered:
            ordered.append(area)
    return ordered


def _attraction_to_activity(att: dict, sort_order: int) -> dict:
    """Convert attraction dict to activity structure."""
    price = _get_attr(att, "price")
    if price is None:
        prov = _get_attr(att, "provider_price")
        price = prov.get("amount", 0) if isinstance(prov, dict) else 0
    if not isinstance(price, (int, float)):
        price = float(price) if price else 0
    return {
        "name": _get_attr(att, "name", "Activity"),
        "emoji": _get_attr(att, "emoji", "📍"),
        "provider": _get_attr(att, "provider") or _get_attr(att, "provider_name", ""),
        "time_start": _get_attr(att, "time_start", "09:00"),
        "time_end": _get_attr(att, "time_end", "12:00"),
        "price": float(price),
        "currency": "NZD",
        "booking_status": "not-booked",
        "sort_order": sort_order,
    }


def _make_accommodation(name: str, location: str) -> dict:
    """Build accommodation placeholder."""
    return {
        "name": name,
        "emoji": "🏨",
        "address": "",
        "check_in": "",
        "check_out": "",
    }


def _make_transport(origin: str, destination: str, distance: str, duration: str) -> dict:
    """Build transport segment."""
    return {
        "mode": "drive",
        "emoji": "🚗",
        "origin": origin,
        "destination": destination,
        "distance": distance,
        "duration": duration,
    }


def _title_for_location(location: str, activities: list) -> str:
    """Generate day title from location and activities."""
    if not activities:
        return f"{location} Day"
    emojis = [a.get("emoji", "📍") for a in activities[:3]]
    suffix = " · ".join(emojis) if emojis else ""
    return f"{location} — {suffix}" if suffix else f"{location} Day"


async def generate_itinerary(planning_state: dict, attractions: list) -> list:
    """
    Generate a day-by-day itinerary from planning selections and NZ attractions.

    Args:
        planning_state: interests, must_dos, dates, driving_preference, group_type, adventure_level, pace
        attractions: list of attraction dicts (name, emoji, region, location_name, price, etc.)

    Returns:
        List of day dicts with day_number, location, title, activities, transport, accommodation.
    """
    entry_point = planning_state.get("entry_point") or "Christchurch"
    pace = planning_state.get("pace") or "balanced"

    # Activities per day based on pace
    activities_per_day = {"relaxed": 1, "balanced": 2, "packed": 3}.get(
        str(pace).lower(), 2
    )
    activities_per_day = min(activities_per_day, 3)

    # Cluster attractions by area
    clusters = _cluster_attractions(attractions)
    areas_with_attractions = set(clusters.keys())
    ordered_areas = _order_areas_by_route(areas_with_attractions)

    # Build list of (area, [attractions]) in route order
    area_attraction_pairs: list[tuple[str, list]] = []
    for area in ordered_areas:
        atts = clusters.get(area, [])
        if atts:
            area_attraction_pairs.append((area, atts))

    # Distribute attractions across days (2-3 per day)
    days_data: list[dict] = []
    day_num = 1
    activity_day_count = 0
    prev_location = entry_point

    # Day 1: Arrival
    days_data.append({
        "day_number": day_num,
        "location": prev_location,
        "title": f"{prev_location} — Arrival",
        "is_flex_day": False,
        "is_arrival": True,
        "is_departure": False,
        "accommodation": _make_accommodation(f"{prev_location} accommodation", prev_location),
        "transport": {},
        "activities": [],
    })
    day_num += 1

    # Process each area
    for area, area_atts in area_attraction_pairs:
        remaining = list(area_atts)
        while remaining:
            # Check if we need a flex day (every 4-5 activity days)
            if activity_day_count > 0 and activity_day_count % 4 == 0:
                days_data.append({
                    "day_number": day_num,
                    "location": prev_location,
                    "title": "Flex Day — Rest or Explore",
                    "is_flex_day": True,
                    "is_arrival": False,
                    "is_departure": False,
                    "accommodation": _make_accommodation(f"{prev_location} accommodation", prev_location),
                    "transport": {},
                    "activities": [],
                })
                day_num += 1

            # Take up to activities_per_day for this day
            batch = remaining[:activities_per_day]
            remaining = remaining[activities_per_day:]

            activities = [
                _attraction_to_activity(a, i) for i, a in enumerate(batch)
            ]
            title = _title_for_location(area, activities)

            # Transport from previous location
            transport = _make_transport(
                prev_location, area, "—", "—"
            ) if prev_location != area else {}

            days_data.append({
                "day_number": day_num,
                "location": area,
                "title": title,
                "is_flex_day": False,
                "is_arrival": False,
                "is_departure": False,
                "accommodation": _make_accommodation(f"{area} accommodation", area),
                "transport": transport,
                "activities": activities,
            })
            prev_location = area
            day_num += 1
            activity_day_count += 1

    # Last day: Departure (back to Christchurch or entry point)
    days_data.append({
        "day_number": day_num,
        "location": prev_location,
        "title": f"{prev_location} — Departure",
        "is_flex_day": False,
        "is_arrival": False,
        "is_departure": True,
        "accommodation": _make_accommodation(f"{prev_location} accommodation", prev_location),
        "transport": _make_transport(prev_location, entry_point, "—", "—") if prev_location != entry_point else {},
        "activities": [],
    })

    log.info(
        "itinerary_generated",
        total_days=len(days_data),
        areas=ordered_areas,
        total_attractions=len(attractions),
    )
    return days_data
