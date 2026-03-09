"""Canonical activity taxonomy for Journey Buddi.

Aligned with TripAdvisor's top-level category structure.
These 9 categories are STRICT — no additions allowed.

Three-level hierarchy:
  1. Category  — chosen during the planning conversation (Level 1)
  2. Activity  — chosen post-chat in the dashboard (Level 2)
  3. Provider  — chosen last, inside the itinerary builder (Level 3)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    slug: str
    label: str
    emoji: str
    description: str


@dataclass(frozen=True)
class Activity:
    slug: str
    label: str
    category_slug: str


# ── The 9 TripAdvisor-aligned categories (strict, no additions) ──────

CATEGORIES: list[Category] = [
    Category(
        "attractions",
        "Attractions",
        "🏛️",
        "Must-see landmarks, nature spots, parks, museums, and points of interest",
    ),
    Category(
        "tours",
        "Tours",
        "🗺️",
        "Guided experiences — cruises, sightseeing, cultural, and wildlife tours",
    ),
    Category(
        "day-trips",
        "Day Trips",
        "🚐",
        "Full-day excursions from a base city to nearby highlights",
    ),
    Category(
        "outdoor-activities",
        "Outdoor Activities",
        "🥾",
        "Active adventures — hiking, water sports, adrenaline, and wildlife encounters",
    ),
    Category(
        "concerts-shows",
        "Concerts & Shows",
        "🎭",
        "Live entertainment, cultural performances, and themed experiences",
    ),
    Category(
        "events",
        "Events",
        "🎪",
        "Festivals, seasonal celebrations, markets, exhibitions, and sporting events",
    ),
    Category(
        "classes-workshops",
        "Classes & Workshops",
        "🎨",
        "Hands-on learning — surf lessons, pottery, photography, cooking, and creative workshops",
    ),
    Category(
        "transportation",
        "Transportation",
        "🚂",
        "Scenic railways, ferries, cable cars, trams, and shuttle services",
    ),
    Category(
        "traveler-resources",
        "Traveler Resources",
        "ℹ️",
        "Visitor centres, information hubs, and practical travel support",
    ),
]


# ── Activities per category ──────────────────────────────────────────
# Derived from TripAdvisor NZ listings + existing Journey Buddi data.

ACTIVITIES: list[Activity] = [
    # ── Attractions ──────────────────────────────────────────────────
    Activity("museums", "Museums", "attractions"),
    Activity("historic-sites", "Historic Sites", "attractions"),
    Activity("nature-wildlife-areas", "Nature & Wildlife Areas", "attractions"),
    Activity("parks-gardens", "Parks & Gardens", "attractions"),
    Activity("hiking-trails", "Hiking Trails", "attractions"),
    Activity("hot-springs-geysers", "Hot Springs & Geysers", "attractions"),
    Activity("caverns-caves", "Caverns & Caves", "attractions"),
    Activity("volcanos", "Volcanos", "attractions"),
    Activity("bodies-of-water", "Bodies of Water", "attractions"),
    Activity("observation-decks-towers", "Observation Decks & Towers", "attractions"),
    Activity("points-of-interest", "Points of Interest & Landmarks", "attractions"),
    Activity("zoos-sanctuaries", "Zoos & Sanctuaries", "attractions"),
    Activity("forests", "Forests", "attractions"),
    Activity("islands", "Islands", "attractions"),
    Activity("geologic-formations", "Geologic Formations", "attractions"),
    Activity("scenic-viewpoints", "Scenic Viewpoints", "attractions"),

    # ── Tours ────────────────────────────────────────────────────────
    Activity("scenic-cruises", "Scenic Cruises", "tours"),
    Activity("wildlife-tours", "Wildlife Tours", "tours"),
    Activity("cultural-tours", "Cultural Tours", "tours"),
    Activity("wine-food-tours", "Wine & Food Tours", "tours"),
    Activity("film-location-tours", "Film Location Tours", "tours"),
    Activity("sightseeing-tours", "Sightseeing Tours", "tours"),
    Activity("eco-tours", "Eco-Tours", "tours"),
    Activity("helicopter-tours", "Helicopter Tours", "tours"),
    Activity("boat-tours", "Boat Tours", "tours"),
    Activity("walking-tours", "Walking Tours", "tours"),
    Activity("guided-cave-tours", "Guided Cave Tours", "tours"),
    Activity("historical-heritage-tours", "Historical & Heritage Tours", "tours"),

    # ── Day Trips ────────────────────────────────────────────────────
    Activity("multi-stop-day-tours", "Multi-Stop Day Tours", "day-trips"),
    Activity("wine-region-day-trips", "Wine Region Day Trips", "day-trips"),
    Activity("nature-day-trips", "Nature & National Park Day Trips", "day-trips"),
    Activity("coastal-day-trips", "Coastal Day Trips", "day-trips"),
    Activity("city-sightseeing-day-trips", "City Sightseeing Day Trips", "day-trips"),
    Activity("cultural-day-trips", "Cultural Day Trips", "day-trips"),

    # ── Outdoor Activities ───────────────────────────────────────────
    Activity("jet-boating", "Jet Boating", "outdoor-activities"),
    Activity("white-water-rafting", "White Water Rafting", "outdoor-activities"),
    Activity("kayaking", "Kayaking", "outdoor-activities"),
    Activity("surfing", "Surfing", "outdoor-activities"),
    Activity("bungy-jumping", "Bungy Jumping", "outdoor-activities"),
    Activity("skydiving", "Skydiving", "outdoor-activities"),
    Activity("zip-lining", "Zip-Lining", "outdoor-activities"),
    Activity("glacier-hiking", "Glacier Hiking", "outdoor-activities"),
    Activity("whale-watching", "Whale Watching", "outdoor-activities"),
    Activity("dolphin-encounters", "Dolphin Encounters", "outdoor-activities"),
    Activity("snorkeling-diving", "Snorkeling & Diving", "outdoor-activities"),
    Activity("hiking-trekking", "Hiking & Trekking", "outdoor-activities"),
    Activity("paragliding", "Paragliding", "outdoor-activities"),
    Activity("canyon-swing", "Canyon Swing", "outdoor-activities"),
    Activity("horse-riding", "Horse Riding", "outdoor-activities"),
    Activity("stand-up-paddleboarding", "Stand-Up Paddleboarding", "outdoor-activities"),
    Activity("fishing", "Fishing", "outdoor-activities"),
    Activity("canyoning", "Canyoning", "outdoor-activities"),
    Activity("hot-air-balloon", "Hot Air Balloon", "outdoor-activities"),
    Activity("luge", "Luge", "outdoor-activities"),
    Activity("zorbing", "Zorbing", "outdoor-activities"),
    Activity("rock-climbing", "Rock Climbing", "outdoor-activities"),
    Activity("sailing", "Sailing", "outdoor-activities"),
    Activity("hot-pools-bathing", "Hot Pools & Bathing", "outdoor-activities"),
    Activity("flyboarding", "Flyboarding", "outdoor-activities"),

    # ── Concerts & Shows ─────────────────────────────────────────────
    Activity("maori-cultural-performances", "Māori Cultural Performances", "concerts-shows"),
    Activity("4wd-quad-adventures", "4WD & Quad Adventures", "concerts-shows"),
    Activity("stargazing-experiences", "Stargazing Experiences", "concerts-shows"),
    Activity("off-road-experiences", "Off-Road Experiences", "concerts-shows"),
    Activity("motorsport-experiences", "Motorsport Experiences", "concerts-shows"),
    Activity("live-music", "Live Music & Concerts", "concerts-shows"),
    Activity("escape-rooms", "Escape Rooms", "concerts-shows"),

    # ── Events ───────────────────────────────────────────────────────
    Activity("cultural-festivals", "Cultural Festivals", "events"),
    Activity("music-festivals", "Music Festivals", "events"),
    Activity("seasonal-events", "Seasonal Events", "events"),
    Activity("markets", "Markets & Fairs", "events"),
    Activity("art-exhibitions", "Art Exhibitions & Galleries", "events"),
    Activity("sporting-events", "Sporting Events", "events"),
    Activity("food-drink-festivals", "Food & Drink Festivals", "events"),

    # ── Classes & Workshops ──────────────────────────────────────────
    Activity("surf-lessons", "Surf Lessons", "classes-workshops"),
    Activity("photography-workshops", "Photography Workshops", "classes-workshops"),
    Activity("pottery-art-classes", "Pottery & Art Classes", "classes-workshops"),
    Activity("special-effects-workshops", "Special Effects Workshops (Wētā)", "classes-workshops"),
    Activity("cooking-classes", "Cooking Classes", "classes-workshops"),
    Activity("mtb-coaching", "Mountain Bike Coaching", "classes-workshops"),
    Activity("farm-experiences", "Farm Experiences", "classes-workshops"),
    Activity("flight-experiences", "Flight Experiences", "classes-workshops"),
    Activity("dirt-bike-tours", "Dirt Bike Tours", "classes-workshops"),

    # ── Transportation ───────────────────────────────────────────────
    Activity("scenic-railways", "Scenic Railways", "transportation"),
    Activity("ferries", "Ferries", "transportation"),
    Activity("cable-cars-gondolas", "Cable Cars & Gondolas", "transportation"),
    Activity("trams", "Trams", "transportation"),
    Activity("water-taxis", "Water Taxis", "transportation"),
    Activity("shuttles", "Shuttles", "transportation"),
    Activity("rail-services", "Rail Services", "transportation"),
    Activity("bus-services", "Bus Services", "transportation"),

    # ── Traveler Resources ───────────────────────────────────────────
    Activity("visitor-centres", "Visitor Centres", "traveler-resources"),
    Activity("information-centres", "Information Centres", "traveler-resources"),
    Activity("libraries", "Libraries", "traveler-resources"),
    Activity("heritage-centres", "Heritage Centres", "traveler-resources"),
]


# ── Lookup indexes (built once at import time) ──────────────────────────

_CATEGORY_BY_SLUG: dict[str, Category] = {c.slug: c for c in CATEGORIES}
_ACTIVITY_BY_SLUG: dict[str, Activity] = {a.slug: a for a in ACTIVITIES}
_ACTIVITIES_BY_CATEGORY: dict[str, list[Activity]] = {}
for _a in ACTIVITIES:
    _ACTIVITIES_BY_CATEGORY.setdefault(_a.category_slug, []).append(_a)

_LABEL_TO_CATEGORY_SLUG: dict[str, str] = {c.label: c.slug for c in CATEGORIES}


def get_category(slug: str) -> Category | None:
    return _CATEGORY_BY_SLUG.get(slug)


def get_activity(slug: str) -> Activity | None:
    return _ACTIVITY_BY_SLUG.get(slug)


def get_activities_for_category(category_slug: str) -> list[Activity]:
    return _ACTIVITIES_BY_CATEGORY.get(category_slug, [])


def get_category_slug_for_label(label: str) -> str | None:
    """Map a UI label like 'Attractions' → 'attractions'."""
    return _LABEL_TO_CATEGORY_SLUG.get(label)


def get_category_for_activity(activity_slug: str) -> str | None:
    act = _ACTIVITY_BY_SLUG.get(activity_slug)
    return act.category_slug if act else None


def get_activity_label(activity_slug: str) -> str | None:
    act = _ACTIVITY_BY_SLUG.get(activity_slug)
    return act.label if act else None


def validate_attraction_tags(category: str, activity: str) -> list[str]:
    """Return list of validation errors (empty = valid)."""
    errors: list[str] = []
    cat = _CATEGORY_BY_SLUG.get(category)
    if not cat:
        errors.append(f"Unknown category: '{category}'")
        return errors

    act = _ACTIVITY_BY_SLUG.get(activity)
    if not act:
        errors.append(f"Unknown activity: '{activity}'")
        return errors

    if act.category_slug != category:
        errors.append(
            f"Activity '{activity}' belongs to '{act.category_slug}', "
            f"not '{category}'"
        )
    return errors
