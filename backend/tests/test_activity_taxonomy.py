"""Tests for the unified activity taxonomy and derived maps."""
import pytest

from app.data.activity_taxonomy import (
    CATEGORIES,
    ACTIVITIES,
    get_activity,
    get_category,
    get_activities_for_category,
    get_category_for_activity,
    validate_attraction_tags,
)
from app.data.nz_attractions import NZ_ATTRACTIONS
from app.agents.tools import (
    CANONICAL_CATEGORIES,
    ACTIVITY_OPTIONS,
    ACTIVITY_LOCATION_MAP,
)


class TestTaxonomyRegistry:
    def test_categories_count(self):
        assert len(CATEGORIES) == 12

    def test_category_slugs_unique(self):
        slugs = [c.slug for c in CATEGORIES]
        assert len(slugs) == len(set(slugs))

    def test_activity_slugs_unique(self):
        slugs = [a.slug for a in ACTIVITIES]
        assert len(slugs) == len(set(slugs))

    def test_every_activity_has_valid_category(self):
        for act in ACTIVITIES:
            cat = get_category(act.category_slug)
            assert cat is not None, f"Activity '{act.slug}' references unknown category '{act.category_slug}'"

    def test_get_category_returns_none_for_unknown(self):
        assert get_category("nonexistent") is None

    def test_get_activity_returns_none_for_unknown(self):
        assert get_activity("nonexistent") is None


class TestAttractionTags:
    def test_all_attractions_have_category_and_activity(self):
        for att in NZ_ATTRACTIONS:
            assert "category" in att, f"{att['slug']} missing 'category'"
            assert "activity" in att, f"{att['slug']} missing 'activity'"

    def test_all_tags_are_valid(self):
        for att in NZ_ATTRACTIONS:
            errors = validate_attraction_tags(att["category"], att["activity"])
            assert not errors, f"{att['slug']}: {errors}"

    def test_no_duplicate_slugs(self):
        slugs = [a["slug"] for a in NZ_ATTRACTIONS]
        assert len(slugs) == len(set(slugs))

    def test_attraction_count(self):
        assert len(NZ_ATTRACTIONS) == 75

    def test_every_category_has_attractions(self):
        cats_in_data = {a["category"] for a in NZ_ATTRACTIONS}
        for cat in CATEGORIES:
            assert cat.slug in cats_in_data, f"No attractions for category '{cat.slug}'"


class TestDerivedMaps:
    def test_canonical_categories_match_taxonomy(self):
        tax_labels = [c.label for c in CATEGORIES]
        assert CANONICAL_CATEGORIES == tax_labels

    def test_activity_options_keys_are_category_labels(self):
        for key in ACTIVITY_OPTIONS:
            assert key in CANONICAL_CATEGORIES, f"ACTIVITY_OPTIONS key '{key}' not a canonical category"

    def test_activity_options_covers_all_categories_with_data(self):
        cats_in_data = set()
        for att in NZ_ATTRACTIONS:
            cat = get_category(att["category"])
            if cat:
                cats_in_data.add(cat.label)
        for cat_label in cats_in_data:
            assert cat_label in ACTIVITY_OPTIONS, f"Category '{cat_label}' has data but no ACTIVITY_OPTIONS entry"

    def test_activity_options_only_lists_activities_with_data(self):
        activities_with_data = {a["activity"] for a in NZ_ATTRACTIONS}
        for cat_label, act_labels in ACTIVITY_OPTIONS.items():
            for act_label in act_labels:
                act_obj = next((a for a in ACTIVITIES if a.label == act_label), None)
                assert act_obj is not None, f"Activity label '{act_label}' not in taxonomy"
                assert act_obj.slug in activities_with_data, (
                    f"Activity '{act_label}' in ACTIVITY_OPTIONS but no attractions tagged with it"
                )

    def test_location_map_has_entries_for_data_activities(self):
        activities_with_data = set()
        for att in NZ_ATTRACTIONS:
            act = get_activity(att["activity"])
            if act:
                activities_with_data.add(act.label)
        for act_label in activities_with_data:
            assert act_label in ACTIVITY_LOCATION_MAP, (
                f"Activity '{act_label}' has data but no ACTIVITY_LOCATION_MAP entry"
            )

    def test_location_map_entries_have_required_fields(self):
        required_keys = {"location", "name", "region", "route_fit", "highlight"}
        for act_label, entries in ACTIVITY_LOCATION_MAP.items():
            for entry in entries:
                missing = required_keys - set(entry.keys())
                assert not missing, f"{act_label}: entry missing keys {missing}"


class TestLocationNormalization:
    """Verify that messy location_name values have been normalized."""

    def test_no_slash_locations(self):
        for att in NZ_ATTRACTIONS:
            loc = att.get("location_name", "")
            assert " / " not in loc, f"{att['slug']} has unnormalized location '{loc}'"

    def test_no_comma_qualified_locations(self):
        known_ok = {"Aoraki/Mt Cook Village"}
        for att in NZ_ATTRACTIONS:
            loc = att.get("location_name", "")
            if loc in known_ok:
                continue
            assert ", " not in loc, f"{att['slug']} has comma-qualified location '{loc}'"
