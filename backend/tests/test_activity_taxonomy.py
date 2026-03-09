"""Tests for the unified activity taxonomy."""
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
from app.agents.tools import CANONICAL_CATEGORIES


class TestTaxonomyRegistry:
    def test_categories_count(self):
        assert len(CATEGORIES) == 9

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

    def test_every_category_has_activities(self):
        for cat in CATEGORIES:
            acts = get_activities_for_category(cat.slug)
            assert len(acts) >= 1, f"Category '{cat.slug}' has no activities defined"


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

    def test_attractions_use_new_categories(self):
        valid_slugs = {c.slug for c in CATEGORIES}
        for att in NZ_ATTRACTIONS:
            assert att["category"] in valid_slugs, (
                f"{att['slug']} uses unknown category '{att['category']}'"
            )


class TestCanonicalCategories:
    def test_canonical_categories_match_taxonomy(self):
        tax_labels = [c.label for c in CATEGORIES]
        canonical_labels = [c["label"] for c in CANONICAL_CATEGORIES]
        assert canonical_labels == tax_labels

    def test_canonical_categories_have_descriptions(self):
        for cat in CANONICAL_CATEGORIES:
            assert cat["description"], f"Category '{cat['label']}' missing description"


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
