"""Generate day-by-day itineraries from planning state and selected attractions."""
from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger()

# Route orders by island (clockwise)
SOUTH_ISLAND_ROUTE = [
    "Christchurch", "Akaroa", "Kaikoura", "Hanmer Springs",
    "Nelson", "Abel Tasman", "West Coast", "Punakaiki",
    "Hokitika", "Franz Josef", "Wanaka", "Queenstown",
    "Milford Sound", "Te Anau", "Dunedin", "Lake Tekapo",
    "Aoraki/Mt Cook",
]

NORTH_ISLAND_ROUTE = [
    "Auckland", "Waiheke Island", "Coromandel", "Hahei", "Whitianga",
    "Matamata", "Rotorua", "Taupo", "Tongariro", "Taranaki",
    "Waitomo", "Putaruru", "Bay of Plenty",
]

LOCATION_KEYWORDS: dict[str, list[str]] = {
    # South Island
    "Christchurch": ["christchurch", "lyttelton", "canterbury"],
    "Akaroa": ["akaroa"],
    "Kaikoura": ["kaikoura"],
    "Hanmer Springs": ["hanmer", "hanmer springs"],
    "Nelson": ["nelson", "motueka", "marlborough", "blenheim"],
    "Abel Tasman": ["abel tasman", "kaiteriteri", "marahau", "nelson-tasman"],
    "West Coast": ["west coast", "greymouth"],
    "Punakaiki": ["punakaiki", "pancake rocks"],
    "Hokitika": ["hokitika"],
    "Franz Josef": ["franz josef", "fox glacier", "glacier", "west-coast"],
    "Wanaka": ["wanaka", "cardrona", "treble cone", "makarora", "haast"],
    "Queenstown": ["queenstown", "arrowtown", "glenorchy", "gibbston", "otago"],
    "Milford Sound": ["milford", "milford sound", "fiordland", "southland-fiordland"],
    "Te Anau": ["te anau", "manapouri"],
    "Dunedin": ["dunedin", "otago peninsula", "oamaru"],
    "Lake Tekapo": ["tekapo", "takapo"],
    "Aoraki/Mt Cook": ["aoraki", "mt cook", "mount cook", "hooker valley"],
    # North Island
    "Auckland": ["auckland"],
    "Waiheke Island": ["waiheke"],
    "Coromandel": ["coromandel"],
    "Hahei": ["hahei", "cathedral cove", "hot water beach"],
    "Whitianga": ["whitianga", "mercury bay"],
    "Matamata": ["matamata", "hobbiton"],
    "Rotorua": ["rotorua", "wai-o-tapu", "te puia"],
    "Taupo": ["taupo", "huka", "waikato", "wairakei"],
    "Tongariro": ["tongariro", "whakapapa", "national park", "tongariro-central"],
    "Taranaki": ["taranaki", "egmont", "new plymouth"],
    "Waitomo": ["waitomo"],
    "Putaruru": ["putaruru", "blue spring"],
    "Bay of Plenty": ["bay of plenty", "tauranga", "mount maunganui", "kaiate"],
}

DRIVE_TIMES: dict[tuple[str, str], str] = {
    ("Christchurch", "Kaikoura"): "2h30",
    ("Christchurch", "Akaroa"): "1h30",
    ("Kaikoura", "Nelson"): "3h30",
    ("Nelson", "Abel Tasman"): "1h",
    ("Abel Tasman", "Punakaiki"): "4h",
    ("Punakaiki", "Hokitika"): "1h30",
    ("Hokitika", "Franz Josef"): "2h",
    ("Franz Josef", "Wanaka"): "4h",
    ("Wanaka", "Queenstown"): "1h15",
    ("Queenstown", "Te Anau"): "2h",
    ("Te Anau", "Milford Sound"): "2h",
    ("Queenstown", "Dunedin"): "4h",
    ("Dunedin", "Lake Tekapo"): "4h",
    ("Lake Tekapo", "Aoraki/Mt Cook"): "1h",
    ("Aoraki/Mt Cook", "Christchurch"): "4h",
    ("Auckland", "Waiheke Island"): "0h40 (ferry)",
    ("Auckland", "Matamata"): "2h",
    ("Matamata", "Rotorua"): "1h",
    ("Rotorua", "Taupo"): "1h",
    ("Taupo", "Tongariro"): "1h",
    ("Auckland", "Waitomo"): "2h30",
    ("Waitomo", "Rotorua"): "2h",
    ("Auckland", "Hahei"): "2h30",
    ("Hahei", "Rotorua"): "2h30",
    ("Taupo", "Taranaki"): "3h",
    ("Rotorua", "Putaruru"): "0h45",
}


def _get_attr(attraction: dict, key: str, default=None):
    if isinstance(attraction, dict):
        return attraction.get(key, default)
    return getattr(attraction, key, default)


def _match_to_route_area(location: str) -> str:
    loc_lower = location.lower() if location else ""
    for area, keywords in LOCATION_KEYWORDS.items():
        for kw in keywords:
            if kw in loc_lower:
                return area
    return location or "Unknown"


def _get_drive_time(origin: str, destination: str) -> str:
    if origin == destination:
        return ""
    return (
        DRIVE_TIMES.get((origin, destination))
        or DRIVE_TIMES.get((destination, origin))
        or "—"
    )


def _order_areas(areas: set[str], route_direction: str = "clockwise") -> list[str]:
    combined_route = NORTH_ISLAND_ROUTE + SOUTH_ISLAND_ROUTE
    if route_direction == "counter-clockwise":
        combined_route = list(reversed(combined_route))

    ordered = [area for area in combined_route if area in areas]
    for area in sorted(areas):
        if area not in ordered:
            ordered.append(area)
    return ordered


def _filter_attractions(
    attractions: list[dict],
    interest_categories: list[str],
    interest_details: dict[str, list[str]],
) -> list[dict]:
    """Filter attractions to only those matching user interests."""
    if not interest_categories:
        return attractions

    category_type_map = {
        "Mountains & Hiking": {"hiking", "alpine", "scenic"},
        "Ocean & Marine Life": {"marine", "wildlife", "cruise", "kayaking"},
        "Beaches & Coast": {"beach", "coastal", "swimming"},
        "Volcanoes & Geothermal": {"volcanic", "geothermal"},
        "Nature & Wildlife": {"nature", "wildlife", "cave"},
        "Food & Wine": {"wine", "food"},
        "Adrenaline & Thrills": {"adventure", "bungy", "adrenaline", "skydive", "jet-boat", "zipline", "rafting", "canyoning", "swing", "paragliding", "balloon"},
        "Culture & History": {"cultural", "film", "film-location"},
        "Photography & Scenery": {"scenic", "photography", "viewpoint"},
        "Stargazing & Dark Skies": {"stargazing"},
        "Water Sports": {"kayaking", "water-sport", "swimming"},
        "Hot Springs & Relaxation": {"spa", "relaxation", "geothermal"},
    }

    wanted_types: set[str] = set()
    for cat in interest_categories:
        wanted_types |= category_type_map.get(cat, set())

    if not wanted_types:
        return attractions

    filtered = []
    for att in attractions:
        att_types = set(_get_attr(att, "types") or [])
        if att_types & wanted_types:
            filtered.append(att)

    return filtered if filtered else attractions


def _build_planned_activities(
    activity_locations: dict[str, str],
    selected_providers: dict[str, dict],
    attractions: list[dict],
) -> dict[str, list[dict]]:
    """Build a location → [activity_dicts] mapping from planning state."""
    location_activities: dict[str, list[dict]] = {}

    attractions_by_name_lower = {}
    for att in attractions:
        name = _get_attr(att, "name") or ""
        attractions_by_name_lower[name.lower()] = att

    for activity, location in activity_locations.items():
        area = _match_to_route_area(location)
        if area not in location_activities:
            location_activities[area] = []

        provider = selected_providers.get(activity, {})
        provider_name = provider.get("name", "") if isinstance(provider, dict) else ""

        att_match = None
        search_terms = [activity.lower(), provider_name.lower()]
        for term in search_terms:
            if term and term in attractions_by_name_lower:
                att_match = attractions_by_name_lower[term]
                break

        price = 0.0
        duration = 2.0
        booking = False
        if att_match:
            logistics = _get_attr(att_match, "logistics") or {}
            cost_info = logistics.get("estimated_cost_nzd", {})
            price = float(cost_info.get("adult", 0)) if isinstance(cost_info, dict) else 0.0
            duration = float(_get_attr(att_match, "duration_min") or 2.0)
            booking = bool(_get_attr(att_match, "booking_required"))

        location_activities[area].append({
            "name": activity,
            "emoji": "🎯",
            "provider": provider_name,
            "time_start": "09:00",
            "time_end": "12:00",
            "price": price,
            "currency": "NZD",
            "booking_status": "needs-booking" if booking else "not-booked",
            "sort_order": len(location_activities[area]),
            "duration_hours": duration,
        })

    return location_activities


def _add_sightseeing(
    location_activities: dict[str, list[dict]],
    location_summary: dict[str, dict[str, Any]],
    attractions: list[dict],
) -> dict[str, list[dict]]:
    """Add 'also nearby' sightseeing activities from the location summary."""
    for location, summary in location_summary.items():
        area = _match_to_route_area(location)
        sightseeing = summary.get("sightseeing", [])
        if not sightseeing:
            continue

        existing_names = {
            a["name"].lower() for a in location_activities.get(area, [])
        }

        for item in sightseeing[:3]:
            if item.lower() not in existing_names:
                if area not in location_activities:
                    location_activities[area] = []
                location_activities[area].append({
                    "name": item,
                    "emoji": "🎁",
                    "provider": "",
                    "time_start": "",
                    "time_end": "",
                    "price": 0.0,
                    "currency": "NZD",
                    "booking_status": "not-booked",
                    "sort_order": len(location_activities[area]),
                    "is_sightseeing": True,
                })

    return location_activities


def _schedule_activities(activities: list[dict], start_hour: int = 9) -> list[dict]:
    """Assign time slots to activities based on duration."""
    current_hour = start_hour
    for act in activities:
        duration = act.pop("duration_hours", 2.0)
        act["time_start"] = f"{int(current_hour):02d}:{int((current_hour % 1) * 60):02d}"
        end_hour = current_hour + duration
        act["time_end"] = f"{int(end_hour):02d}:{int((end_hour % 1) * 60):02d}"
        current_hour = end_hour + 0.5  # 30min gap
    return activities


async def generate_itinerary(planning_state: dict, attractions: list) -> list:
    """
    Generate a day-by-day itinerary connected to planning state.

    Uses activity_locations, days_per_location, selected_providers, and
    interest data to build a personalized itinerary rather than
    dumping all attractions.
    """
    entry_point = planning_state.get("entry_point") or "Christchurch"
    route_direction = planning_state.get("route_direction") or "clockwise"
    pace = planning_state.get("pace") or "balanced"

    interest_categories = planning_state.get("interest_categories", [])
    interest_details = planning_state.get("interest_details", {})
    activity_locations = planning_state.get("activity_locations", {})
    selected_providers = planning_state.get("selected_providers", {})
    location_summary = planning_state.get("location_summary", {})
    days_per_location = planning_state.get("days_per_location", {})

    max_activities_per_day = {"relaxed": 1, "balanced": 2, "packed": 3}.get(
        str(pace).lower(), 2
    )

    if activity_locations:
        location_activities = _build_planned_activities(
            activity_locations, selected_providers, attractions,
        )
        if location_summary:
            location_activities = _add_sightseeing(
                location_activities, location_summary, attractions,
            )
    else:
        filtered = _filter_attractions(attractions, interest_categories, interest_details)
        location_activities: dict[str, list[dict]] = {}
        for att in filtered:
            loc = ""
            for key in ("location_name", "region", "name"):
                val = _get_attr(att, key)
                if val:
                    loc = str(val)
                    break
            area = _match_to_route_area(loc)
            if area not in location_activities:
                location_activities[area] = []

            logistics = _get_attr(att, "logistics") or {}
            cost_info = logistics.get("estimated_cost_nzd", {})
            price = float(cost_info.get("adult", 0)) if isinstance(cost_info, dict) else 0.0

            location_activities[area].append({
                "name": _get_attr(att, "name", "Activity"),
                "emoji": "📍",
                "provider": "",
                "time_start": "09:00",
                "time_end": "12:00",
                "price": price,
                "currency": "NZD",
                "booking_status": "not-booked",
                "sort_order": len(location_activities[area]),
                "duration_hours": float(_get_attr(att, "duration_min") or 2.0),
            })

    areas_with_activities = set(location_activities.keys())
    ordered_areas = _order_areas(areas_with_activities, route_direction)

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
        "accommodation": {"name": f"{prev_location} accommodation", "emoji": "🏨"},
        "transport": {},
        "activities": [],
    })
    day_num += 1

    for area in ordered_areas:
        area_acts = location_activities.get(area, [])
        if not area_acts:
            continue

        allocated_days = days_per_location.get(area, 0)
        if not allocated_days:
            allocated_days = max(1, (len(area_acts) + max_activities_per_day - 1) // max_activities_per_day)

        remaining = list(area_acts)
        days_for_area = 0

        while remaining and days_for_area < allocated_days:
            if activity_day_count > 0 and activity_day_count % 5 == 0:
                days_data.append({
                    "day_number": day_num,
                    "location": area,
                    "title": "Flex Day — Rest or Explore",
                    "is_flex_day": True,
                    "is_arrival": False,
                    "is_departure": False,
                    "accommodation": {"name": f"{area} accommodation", "emoji": "🏨"},
                    "transport": {},
                    "activities": [],
                })
                day_num += 1

            batch = remaining[:max_activities_per_day]
            remaining = remaining[max_activities_per_day:]

            scheduled = _schedule_activities(list(batch))

            drive_time = _get_drive_time(prev_location, area)
            transport = {
                "mode": "drive",
                "emoji": "🚗",
                "origin": prev_location,
                "destination": area,
                "duration": drive_time,
            } if prev_location != area and drive_time else {}

            activity_names = [a["name"] for a in scheduled[:2]]
            title = f"{area} — {' · '.join(activity_names)}" if activity_names else f"{area} Day"

            days_data.append({
                "day_number": day_num,
                "location": area,
                "title": title,
                "is_flex_day": False,
                "is_arrival": False,
                "is_departure": False,
                "accommodation": {"name": f"{area} accommodation", "emoji": "🏨"},
                "transport": transport,
                "activities": scheduled,
            })
            prev_location = area
            day_num += 1
            days_for_area += 1
            activity_day_count += 1

        if remaining:
            for act in remaining:
                act.pop("duration_hours", None)
            days_data[-1]["activities"].extend(remaining)

    # Final day: departure
    days_data.append({
        "day_number": day_num,
        "location": prev_location,
        "title": f"{prev_location} — Departure",
        "is_flex_day": False,
        "is_arrival": False,
        "is_departure": True,
        "accommodation": {"name": f"{prev_location} accommodation", "emoji": "🏨"},
        "transport": {
            "mode": "drive",
            "emoji": "🚗",
            "origin": prev_location,
            "destination": entry_point,
            "duration": _get_drive_time(prev_location, entry_point),
        } if prev_location != entry_point else {},
        "activities": [],
    })

    log.info(
        "itinerary_generated",
        total_days=len(days_data),
        areas=ordered_areas,
        total_activities=sum(len(location_activities.get(a, [])) for a in ordered_areas),
        used_planning_state=bool(activity_locations),
    )
    return days_data
