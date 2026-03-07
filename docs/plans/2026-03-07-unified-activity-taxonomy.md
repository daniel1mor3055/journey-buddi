# Unified Activity Taxonomy — Implementation Plan

**Goal:** Consolidate three disconnected activity layers (ACTIVITY_OPTIONS, ACTIVITY_LOCATION_MAP, NZ_ATTRACTIONS.types) into a single taxonomy where the attraction data IS the source of truth for all UI options.

**Architecture:** Each attraction gets tagged with one `category` (from 12 canonical categories) and one `activity` (the specific activity within that category). The existing hardcoded dicts (`ACTIVITY_OPTIONS`, `ACTIVITY_LOCATION_MAP`, `SIGHTSEEING_BY_LOCATION`) are replaced by functions that derive their values from the attraction data at startup. The `_build_provider_db()` manual mapping is eliminated.

**Tech Stack:** Python, SQLAlchemy, Alembic, existing NZ attraction data files.

---

## Problem Summary

### Current state: 3 disconnected layers

| Layer | Location | What it does | Vocabulary |
|-------|----------|-------------|-----------|
| `ACTIVITY_OPTIONS` | `tools.py` L357-406 | Hardcoded dict: 12 categories → lists of activity strings | Human labels: "Day hikes to summits", "Bungy jumping" |
| `ACTIVITY_LOCATION_MAP` | `tools.py` L582-699 | Hardcoded dict: activity → locations/venues | Repeats some labels, not all |
| `NZ_ATTRACTIONS.types` | `nz_attractions*.py` | 50 unique lowercase tags on 75 attractions | Lowercase tags: "bungy", "hiking", "scenic" |

Bridged by a fragile manual map in `_build_provider_db()` that only covers ~16 of 50 tags.

### Consequences
- Many attractions can never be surfaced to users (no mapping from their types to ACTIVITY_OPTIONS)
- Overlapping activities across categories (e.g. "Whale watching" appears in both "Ocean & Marine Life" and "Nature & Wildlife")
- Inconsistent location names (e.g. "Lake Tekapo" vs "Lake Tekapo / Takapō", "Waiheke Island" vs "Waiheke Island, Auckland")
- Adding a new attraction requires updating 3-4 separate places

---

## Canonical Taxonomy

### 12 Categories → Activities

Each attraction will be tagged with exactly ONE `(category, activity)` pair.

| Category | Activities (canonical names) |
|----------|---------------------------|
| Mountains & Hiking | day-hike, multi-day-trek, coastal-walk, forest-walk, glacier-hike, ridge-walk |
| Ocean & Marine Life | whale-watching, dolphin-swim, snorkeling, scuba-diving, kayaking, sailing, surfing |
| Beaches & Coast | beach-walk, coastal-hike, rock-pooling, beach-camping, cove-exploration |
| Volcanoes & Geothermal | hot-springs, mud-pools, geysers, volcanic-crater-walk, geothermal-park |
| Nature & Wildlife | penguin-colony, seal-watching, birdwatching, glowworm-caves, kiwi-spotting, waterfall-walk, scenic-walk |
| Food & Wine | vineyard-tour, wine-tasting, cooking-class, food-market, craft-beer-tour, farm-to-table |
| Adrenaline & Thrills | skydiving, bungy-jumping, jet-boating, white-water-rafting, zip-lining, canyoning, paragliding, swing, horse-riding, hot-air-balloon, canyon-swing, luge |
| Culture & History | maori-cultural-experience, museum, historical-site, art-gallery, heritage-trail, film-location |
| Photography & Scenery | landscape-photography, sunrise-sunset-spot, aerial-photography, wildlife-photography, scenic-drive, scenic-viewpoint |
| Stargazing & Dark Skies | stargazing-tour, dark-sky-reserve, astrophotography, aurora-viewing |
| Water Sports | kayaking, surfing, stand-up-paddleboarding, jet-skiing, fishing, sailing |
| Hot Springs & Relaxation | natural-hot-springs, spa-experience, thermal-pool, wellness-retreat |

### Overlap resolution rules
- An attraction belongs to exactly ONE category (its primary identity)
- The `types` array is kept for search/filtering but `category` + `activity` are the canonical classification
- When an attraction spans categories (e.g. Te Puia = cultural + geothermal), pick the primary identity and note the secondary in `types`

---

## Implementation Tasks

### Task 1: Create taxonomy registry (`backend/app/data/activity_taxonomy.py`)

**Files:** `backend/app/data/activity_taxonomy.py` (new)

A single Python module that defines:
- `CATEGORIES`: ordered list of category dicts with slug, label, emoji
- `ACTIVITIES`: dict mapping category_slug → list of activity dicts with slug, label
- Helper: `get_category_for_activity(activity_slug) → category_slug`
- Helper: `get_activity_label(activity_slug) → str`

### Task 2: Tag all 75 attractions with `category` + `activity`

**Files:** All 5 `nz_attractions*.py` files

Add two new keys to each attraction dict:
- `"category"`: one of the 12 category slugs
- `"activity"`: one of the activity slugs from that category

Also normalize `location_name` inconsistencies:
- `"Lake Tekapo / Takapō"` → `"Lake Tekapo"`
- `"Waiheke Island, Auckland"` → `"Waiheke Island"`
- `"Waitomo, Waikato"` → `"Waitomo"`
- `"Kaikōura"` → `"Kaikoura"` (match ACTIVITY_LOCATION_MAP)

### Task 3: Add `category` + `activity` columns to Attraction model + migration

**Files:** `backend/app/models/attraction.py`, new Alembic migration

Add:
- `category: Mapped[str]` (String(50), nullable=False, indexed)
- `activity: Mapped[str]` (String(100), nullable=False, indexed)

### Task 4: Build derived maps in `tools.py`

**Files:** `backend/app/agents/tools.py`

Replace hardcoded dicts with functions that build from `NZ_ATTRACTIONS`:

```python
def _build_activity_options() -> dict[str, list[str]]:
    """Build ACTIVITY_OPTIONS from attraction data — category → unique activities."""

def _build_activity_location_map() -> dict[str, list[dict]]:
    """Build ACTIVITY_LOCATION_MAP from attraction data — activity → locations."""

def _build_sightseeing_map() -> dict[str, list[str]]:
    """Keep SIGHTSEEING_BY_LOCATION as-is (not attraction-derived)."""
```

Remove:
- Hardcoded `ACTIVITY_OPTIONS` dict
- Hardcoded `ACTIVITY_LOCATION_MAP` dict
- `_build_provider_db()` manual mapping
- `activity_type_map` in `_build_provider_db()`

### Task 5: Update orchestrator fallbacks

**Files:** `backend/app/agents/orchestrator.py`

The orchestrator's `_FIELD_FALLBACKS` for `interest_categories` uses the 12 category labels which remain unchanged. The `_field_fallback` method for `interest_deep_dive` and `activity_location` already reads from `ACTIVITY_OPTIONS` and `ACTIVITY_LOCATION_MAP` — once those are derived from data, the orchestrator works automatically.

### Task 6: Validation + tests

**Files:** `backend/tests/test_activity_taxonomy.py` (new)

- Test: every attraction has a valid `category` and `activity`
- Test: every `activity` belongs to its claimed `category`
- Test: derived `ACTIVITY_OPTIONS` covers all activities from the data
- Test: derived `ACTIVITY_LOCATION_MAP` has entries for all activities that have real locations
- Test: no duplicate slugs across attractions
- Test: `location_name` values are normalized (no trailing location specifiers)

---

## Execution Order

1. Task 1 → Task 2 → commit (taxonomy + data tagging)
2. Task 3 → commit (model + migration)
3. Task 4 → Task 5 → commit (derived maps + orchestrator)
4. Task 6 → commit (tests)
