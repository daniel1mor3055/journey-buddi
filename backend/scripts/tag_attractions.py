#!/usr/bin/env python3
"""One-shot script to add category + activity tags and normalize location_names.

Tags use the 9 TripAdvisor-aligned categories introduced in the 3-level
activity design shift (2026-03-09). All 75 attractions are already tagged
in the data files; this script can be re-run to validate or to re-apply
tags after a data reset.

Run from backend/:
    PYTHONPATH=. venv/bin/python3 scripts/tag_attractions.py
"""
import re
import sys
from pathlib import Path

SLUG_TAGS: dict[str, tuple[str, str]] = {
    # ── Core ─────────────────────────────────────────────────────────────
    "nz-milford-sound-cruise":          ("tours", "scenic-cruises"),
    "nz-tongariro-alpine-crossing":     ("attractions", "hiking-trails"),
    "nz-franz-josef-glacier-heli-hike": ("outdoor-activities", "glacier-hiking"),
    "nz-kaikoura-whale-watching":       ("outdoor-activities", "whale-watching"),
    "nz-abel-tasman-day":               ("day-trips", "coastal-day-trips"),
    "nz-lake-tekapo-stargazing":        ("concerts-shows", "stargazing-experiences"),
    "nz-hooker-valley-track":           ("attractions", "hiking-trails"),
    "nz-wai-o-tapu":                    ("attractions", "hot-springs-geysers"),
    "nz-waitomo-glowworm-caves":        ("tours", "guided-cave-tours"),
    "nz-hobbiton":                      ("tours", "film-location-tours"),
    "nz-cathedral-cove":                ("attractions", "scenic-viewpoints"),
    "nz-kawarau-bungy":                 ("outdoor-activities", "bungy-jumping"),
    "nz-otago-peninsula-wildlife":      ("tours", "wildlife-tours"),
    "nz-hot-water-beach":               ("attractions", "hot-springs-geysers"),
    "nz-roys-peak":                     ("attractions", "hiking-trails"),
    "nz-te-puia-rotorua":               ("tours", "cultural-tours"),
    "nz-pancake-rocks-punakaiki":       ("attractions", "scenic-viewpoints"),
    "nz-doubtful-sound-overnight":      ("tours", "scenic-cruises"),

    # ── Adventure ────────────────────────────────────────────────────────
    "nz-nevis-bungy":                   ("outdoor-activities", "bungy-jumping"),
    "nz-nevis-swing":                   ("outdoor-activities", "canyon-swing"),
    "nz-shotover-canyon-swing":         ("outdoor-activities", "canyon-swing"),
    "nz-taupo-bungy-swing":             ("outdoor-activities", "bungy-jumping"),
    "nz-skydive-queenstown":            ("outdoor-activities", "skydiving"),
    "nz-skydive-wanaka":                ("outdoor-activities", "skydiving"),
    "nz-shotover-jet":                  ("outdoor-activities", "jet-boating"),
    "nz-huka-falls-jet":                ("outdoor-activities", "jet-boating"),
    "nz-flyboard-queenstown":           ("outdoor-activities", "flyboarding"),
    "nz-flyboard-taupo":                ("outdoor-activities", "flyboarding"),
    "nz-canyoning-wanaka":              ("outdoor-activities", "canyoning"),
    "nz-rotorua-canopy-tours":          ("outdoor-activities", "zip-lining"),
    "nz-waiheke-ecozip":                ("outdoor-activities", "zip-lining"),
    "nz-ziptrek-queenstown":            ("outdoor-activities", "zip-lining"),
    "nz-paraglide-queenstown":          ("outdoor-activities", "paragliding"),
    "nz-paraglide-wanaka":              ("outdoor-activities", "paragliding"),
    "nz-zorb-rotorua":                  ("outdoor-activities", "zorbing"),
    "nz-whitewater-rafting-kaituna":    ("outdoor-activities", "white-water-rafting"),
    "nz-hot-air-balloon-canterbury":    ("outdoor-activities", "hot-air-balloon"),
    "nz-horse-riding-glenorchy":        ("outdoor-activities", "horse-riding"),
    "nz-horse-riding-pakiri-beach":     ("outdoor-activities", "horse-riding"),
    "nz-horse-riding-tekapo":           ("outdoor-activities", "horse-riding"),

    # ── Nature ───────────────────────────────────────────────────────────
    "nz-tama-lakes-track":              ("attractions", "hiking-trails"),
    "nz-meads-wall":                    ("tours", "film-location-tours"),
    "nz-taranaki-falls":                ("attractions", "hiking-trails"),
    "nz-pouakai-tarn":                  ("attractions", "hiking-trails"),
    "nz-three-sisters-taranaki":        ("attractions", "scenic-viewpoints"),
    "nz-blue-spring-te-waihou":         ("attractions", "nature-wildlife-areas"),
    "nz-aratiatia-rapids":              ("attractions", "nature-wildlife-areas"),
    "nz-bridal-veil-falls":             ("attractions", "nature-wildlife-areas"),
    "nz-kaiate-falls":                  ("attractions", "nature-wildlife-areas"),
    "nz-thunder-creek-falls":           ("attractions", "nature-wildlife-areas"),
    "nz-blue-pools-track":              ("attractions", "hiking-trails"),
    "nz-lake-matheson":                 ("attractions", "scenic-viewpoints"),
    "nz-devils-punchbowl-waterfall":    ("attractions", "nature-wildlife-areas"),
    "nz-redwoods-treewalk-rotorua":     ("attractions", "forests"),
    "nz-hokitika-gorge":                ("attractions", "nature-wildlife-areas"),
    "nz-glow-worm-dell-hokitika":       ("tours", "guided-cave-tours"),
    "nz-key-summit-track":              ("attractions", "hiking-trails"),
    "nz-lake-marian-track":             ("attractions", "hiking-trails"),
    "nz-crown-range-road":              ("attractions", "scenic-viewpoints"),
    "nz-mangapohue-natural-bridge":     ("attractions", "nature-wildlife-areas"),

    # ── Thermal ──────────────────────────────────────────────────────────
    "nz-polynesian-spa-rotorua":        ("outdoor-activities", "hot-pools-bathing"),
    "nz-onsen-hot-pools-queenstown":    ("outdoor-activities", "hot-pools-bathing"),
    "nz-tekapo-springs":                ("outdoor-activities", "hot-pools-bathing"),
    "nz-lost-spring-whitianga":         ("outdoor-activities", "hot-pools-bathing"),
    "nz-wairakei-terraces-taupo":       ("attractions", "hot-springs-geysers"),
    "nz-hells-gate-rotorua":            ("attractions", "hot-springs-geysers"),
    "nz-spa-thermal-park-taupo":        ("outdoor-activities", "hot-pools-bathing"),
    "nz-craters-of-the-moon-taupo":     ("attractions", "hot-springs-geysers"),
    "nz-kuirau-park-rotorua":           ("attractions", "hot-springs-geysers"),

    # ── Cultural ─────────────────────────────────────────────────────────
    "nz-waiheke-island-wine-tours":     ("tours", "wine-food-tours"),
    "nz-marlborough-wine-tours":        ("tours", "wine-food-tours"),
    "nz-central-otago-wine-tours":      ("tours", "wine-food-tours"),
    "nz-auckland-food-tour":            ("tours", "wine-food-tours"),
    "nz-spellbound-glowworm-waitomo":   ("tours", "guided-cave-tours"),
    "nz-hobbiton-evening-banquet":      ("tours", "film-location-tours"),
}

LOCATION_NORMALIZATIONS: dict[str, str] = {
    "Lake Tekapo / Takapō": "Lake Tekapo",
    "Waiheke Island, Auckland": "Waiheke Island",
    "Waitomo, Waikato": "Waitomo",
    "Kaikōura": "Kaikoura",
    "Manapōuri / Te Anau": "Te Anau",
    "Marahau / Kaiteriteri": "Abel Tasman",
    "Putaruru, Waikato": "Putaruru",
    "Aratiatia, Taupo": "Taupo",
    "Raglan, Waikato": "Raglan",
    "Haast Pass, West Coast": "Haast Pass",
    "Makarora, Haast Pass": "Makarora",
    "Fox Glacier, West Coast": "Fox Glacier",
    "Hokitika, West Coast": "Hokitika",
    "Tongaporutu, Taranaki Coast": "Tongaporutu",
    "Crown Range, Queenstown-Wanaka": "Crown Range",
    "Te Puke, Bay of Plenty": "Te Puke",
    "Methven / Canterbury Plains": "Methven",
    "Blenheim, Marlborough": "Marlborough",
    "Gibbston, Queenstown": "Gibbston",
    "Whakapapa Village, Tongariro National Park": "Tongariro",
    "Iwikau Village, Whakapapa Ski Area": "Tongariro",
    "Whitianga, Coromandel": "Whitianga",
    "Hollyford Road, Fiordland": "Fiordland",
    "The Divide, Milford Road": "Fiordland",
}


def process_file(filepath: Path) -> int:
    """Re-apply category/activity tags and normalize location_name.
    Returns count of modified attractions.
    """
    content = filepath.read_text()
    original = content
    modified = 0

    for slug, (category, activity) in SLUG_TAGS.items():
        slug_pattern = f'"slug": "{slug}"'
        if slug_pattern not in content:
            continue

        tag_line = f'        "category": "{category}",\n        "activity": "{activity}",'

        # Check if this slug already has the correct tags
        idx = content.index(slug_pattern)
        nearby = content[idx:idx + 300]
        if f'"category": "{category}"' in nearby and f'"activity": "{activity}"' in nearby:
            continue

        types_pattern = re.compile(
            r'("slug": "' + re.escape(slug) + r'".*?'
            r'"types": \[.*?\]),',
            re.DOTALL,
        )
        match = types_pattern.search(content)
        if match:
            end = match.end()
            content = content[:end] + "\n" + tag_line + content[end:]
            modified += 1

    for old_loc, new_loc in LOCATION_NORMALIZATIONS.items():
        content = content.replace(f'"location_name": "{old_loc}"', f'"location_name": "{new_loc}"')

    if content != original:
        filepath.write_text(content)

    return modified


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "app" / "data"
    files = [
        data_dir / "nz_attractions.py",
        data_dir / "nz_attractions_adventure.py",
        data_dir / "nz_attractions_nature.py",
        data_dir / "nz_attractions_thermal.py",
        data_dir / "nz_attractions_cultural.py",
    ]

    total = 0
    for f in files:
        n = process_file(f)
        print(f"  {f.name}: {n} attractions re-tagged")
        total += n

    print(f"\nTotal: {total} attractions processed")

    print("Validating tags against new 9-category taxonomy...")
    sys.path.insert(0, str(data_dir.parent.parent))
    from app.data.activity_taxonomy import validate_attraction_tags
    from app.data.nz_attractions import NZ_ATTRACTIONS

    errors = []
    for att in NZ_ATTRACTIONS:
        errs = validate_attraction_tags(att.get("category", ""), att.get("activity", ""))
        if errs:
            errors.append(f"  {att['slug']}: {errs}")

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(e)
        sys.exit(1)

    print(f"All {len(NZ_ATTRACTIONS)} attractions valid against the 9-category taxonomy!")


if __name__ == "__main__":
    main()
