"""Canonical activity taxonomy for Journey Buddi.

Single source of truth for categories and activities. All UI options,
location maps, and provider lookups derive from this taxonomy combined
with the attraction data.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    slug: str
    label: str
    emoji: str


@dataclass(frozen=True)
class Activity:
    slug: str
    label: str
    category_slug: str


CATEGORIES: list[Category] = [
    Category("mountains-hiking", "Mountains & Hiking", "🏔️"),
    Category("ocean-marine", "Ocean & Marine Life", "🌊"),
    Category("beaches-coast", "Beaches & Coast", "🏖️"),
    Category("volcanoes-geothermal", "Volcanoes & Geothermal", "🌋"),
    Category("nature-wildlife", "Nature & Wildlife", "🌿"),
    Category("food-wine", "Food & Wine", "🍷"),
    Category("adrenaline-thrills", "Adrenaline & Thrills", "🪂"),
    Category("culture-history", "Culture & History", "📖"),
    Category("photography-scenery", "Photography & Scenery", "📸"),
    Category("stargazing-dark-skies", "Stargazing & Dark Skies", "⭐"),
    Category("water-sports", "Water Sports", "🚣"),
    Category("hot-springs-relaxation", "Hot Springs & Relaxation", "♨️"),
]

ACTIVITIES: list[Activity] = [
    # Mountains & Hiking
    Activity("day-hike", "Day hikes to summits", "mountains-hiking"),
    Activity("multi-day-trek", "Multi-day treks", "mountains-hiking"),
    Activity("forest-walk", "Forest walks", "mountains-hiking"),
    Activity("glacier-hike", "Glacier hikes", "mountains-hiking"),
    Activity("ridge-walk", "Ridge walks", "mountains-hiking"),

    # Ocean & Marine Life
    Activity("whale-watching", "Whale watching", "ocean-marine"),
    Activity("dolphin-swim", "Swim with dolphins", "ocean-marine"),
    Activity("snorkeling", "Snorkeling", "ocean-marine"),
    Activity("scuba-diving", "Scuba diving", "ocean-marine"),

    # Beaches & Coast
    Activity("beach-walk", "Beach walks", "beaches-coast"),
    Activity("coastal-walk", "Coastal walks", "beaches-coast"),
    Activity("rock-pooling", "Rock pooling", "beaches-coast"),
    Activity("beach-camping", "Beach camping", "beaches-coast"),
    Activity("cove-exploration", "Hidden coves exploration", "beaches-coast"),

    # Volcanoes & Geothermal
    Activity("hot-springs", "Hot springs", "volcanoes-geothermal"),
    Activity("mud-pools", "Mud pools", "volcanoes-geothermal"),
    Activity("geysers", "Geysers", "volcanoes-geothermal"),
    Activity("volcanic-crater-walk", "Volcanic crater walks", "volcanoes-geothermal"),
    Activity("geothermal-park", "Geothermal parks", "volcanoes-geothermal"),

    # Nature & Wildlife
    Activity("penguin-colony", "Penguin colonies", "nature-wildlife"),
    Activity("seal-watching", "Seal watching", "nature-wildlife"),
    Activity("birdwatching", "Birdwatching", "nature-wildlife"),
    Activity("glowworm-caves", "Glowworm caves", "nature-wildlife"),
    Activity("kiwi-spotting", "Kiwi spotting", "nature-wildlife"),
    Activity("waterfall-walk", "Waterfall walks", "nature-wildlife"),
    Activity("scenic-walk", "Scenic walks", "nature-wildlife"),
    Activity("scenic-cruise", "Scenic cruises", "nature-wildlife"),
    Activity("wildlife-watching", "Wildlife watching", "nature-wildlife"),

    # Food & Wine
    Activity("vineyard-tour", "Vineyard tours", "food-wine"),
    Activity("wine-tasting", "Wine tasting", "food-wine"),
    Activity("cooking-class", "Cooking classes", "food-wine"),
    Activity("food-market", "Food markets", "food-wine"),
    Activity("craft-beer-tour", "Craft beer tours", "food-wine"),
    Activity("farm-to-table", "Farm-to-table dining", "food-wine"),

    # Adrenaline & Thrills
    Activity("skydiving", "Skydiving", "adrenaline-thrills"),
    Activity("bungy-jumping", "Bungy jumping", "adrenaline-thrills"),
    Activity("jet-boating", "Jet boating", "adrenaline-thrills"),
    Activity("white-water-rafting", "White water rafting", "adrenaline-thrills"),
    Activity("zip-lining", "Zip-lining", "adrenaline-thrills"),
    Activity("canyoning", "Canyoning", "adrenaline-thrills"),
    Activity("paragliding", "Paragliding", "adrenaline-thrills"),
    Activity("canyon-swing", "Canyon swing", "adrenaline-thrills"),
    Activity("horse-riding", "Horse riding", "adrenaline-thrills"),
    Activity("hot-air-balloon", "Hot air balloon", "adrenaline-thrills"),
    Activity("luge", "Luge", "adrenaline-thrills"),
    Activity("zorbing", "Zorbing", "adrenaline-thrills"),

    # Culture & History
    Activity("maori-cultural-experience", "Māori cultural experiences", "culture-history"),
    Activity("museum", "Museums", "culture-history"),
    Activity("historical-site", "Historical sites", "culture-history"),
    Activity("art-gallery", "Art galleries", "culture-history"),
    Activity("heritage-trail", "Heritage trails", "culture-history"),
    Activity("film-location", "Film locations", "culture-history"),

    # Photography & Scenery
    Activity("landscape-photography", "Landscape photography", "photography-scenery"),
    Activity("sunrise-sunset-spot", "Sunrise / sunset spots", "photography-scenery"),
    Activity("aerial-photography", "Aerial photography", "photography-scenery"),
    Activity("wildlife-photography", "Wildlife photography", "photography-scenery"),
    Activity("scenic-drive", "Scenic drives", "photography-scenery"),
    Activity("scenic-viewpoint", "Scenic viewpoints", "photography-scenery"),

    # Stargazing & Dark Skies
    Activity("stargazing-tour", "Stargazing tours", "stargazing-dark-skies"),
    Activity("dark-sky-reserve", "Dark sky reserves", "stargazing-dark-skies"),
    Activity("astrophotography", "Astrophotography", "stargazing-dark-skies"),
    Activity("aurora-viewing", "Aurora viewing", "stargazing-dark-skies"),

    # Water Sports
    Activity("kayaking", "Kayaking", "water-sports"),
    Activity("surfing", "Surfing", "water-sports"),
    Activity("stand-up-paddleboarding", "Stand-up paddleboarding", "water-sports"),
    Activity("jet-skiing", "Jet skiing", "water-sports"),
    Activity("fishing", "Fishing", "water-sports"),
    Activity("sailing", "Sailing", "water-sports"),
    Activity("flyboarding", "Flyboarding", "water-sports"),

    # Hot Springs & Relaxation
    Activity("natural-hot-springs", "Natural hot springs", "hot-springs-relaxation"),
    Activity("spa-experience", "Spa experiences", "hot-springs-relaxation"),
    Activity("thermal-pool", "Thermal pools", "hot-springs-relaxation"),
    Activity("wellness-retreat", "Wellness retreats", "hot-springs-relaxation"),
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
    """Map a UI label like 'Mountains & Hiking' → 'mountains-hiking'."""
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
