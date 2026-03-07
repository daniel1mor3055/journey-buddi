#!/usr/bin/env python3
"""One-shot script to add category + activity tags and normalize location_names.

Run from backend/:
    PYTHONPATH=. venv/bin/python3 scripts/tag_attractions.py
"""
import re
import sys
from pathlib import Path

SLUG_TAGS: dict[str, tuple[str, str]] = {
    # ── Core ─────────────────────────────────────────────────────────────
    "nz-milford-sound-cruise":         ("nature-wildlife", "scenic-cruise"),
    "nz-tongariro-alpine-crossing":    ("mountains-hiking", "day-hike"),
    "nz-franz-josef-glacier-heli-hike":("mountains-hiking", "glacier-hike"),
    "nz-kaikoura-whale-watching":      ("ocean-marine", "whale-watching"),
    "nz-abel-tasman-day":              ("beaches-coast", "coastal-walk"),
    "nz-lake-tekapo-stargazing":       ("stargazing-dark-skies", "stargazing-tour"),
    "nz-hooker-valley-track":          ("mountains-hiking", "day-hike"),
    "nz-wai-o-tapu":                   ("volcanoes-geothermal", "geothermal-park"),
    "nz-waitomo-glowworm-caves":       ("nature-wildlife", "glowworm-caves"),
    "nz-hobbiton":                     ("culture-history", "film-location"),
    "nz-cathedral-cove":               ("beaches-coast", "coastal-walk"),
    "nz-kawarau-bungy":                ("adrenaline-thrills", "bungy-jumping"),
    "nz-otago-peninsula-wildlife":     ("nature-wildlife", "wildlife-watching"),
    "nz-hot-water-beach":              ("volcanoes-geothermal", "hot-springs"),
    "nz-roys-peak":                    ("mountains-hiking", "day-hike"),
    "nz-te-puia-rotorua":              ("culture-history", "maori-cultural-experience"),
    "nz-pancake-rocks-punakaiki":      ("photography-scenery", "scenic-viewpoint"),
    "nz-doubtful-sound-overnight":     ("nature-wildlife", "scenic-cruise"),

    # ── Adventure ────────────────────────────────────────────────────────
    "nz-nevis-bungy":                  ("adrenaline-thrills", "bungy-jumping"),
    "nz-nevis-swing":                  ("adrenaline-thrills", "canyon-swing"),
    "nz-shotover-canyon-swing":        ("adrenaline-thrills", "canyon-swing"),
    "nz-taupo-bungy-swing":           ("adrenaline-thrills", "bungy-jumping"),
    "nz-skydive-queenstown":           ("adrenaline-thrills", "skydiving"),
    "nz-skydive-wanaka":               ("adrenaline-thrills", "skydiving"),
    "nz-shotover-jet":                 ("adrenaline-thrills", "jet-boating"),
    "nz-huka-falls-jet":              ("adrenaline-thrills", "jet-boating"),
    "nz-flyboard-queenstown":          ("water-sports", "flyboarding"),
    "nz-flyboard-taupo":              ("water-sports", "flyboarding"),
    "nz-canyoning-wanaka":             ("adrenaline-thrills", "canyoning"),
    "nz-rotorua-canopy-tours":         ("adrenaline-thrills", "zip-lining"),
    "nz-waiheke-ecozip":               ("adrenaline-thrills", "zip-lining"),
    "nz-ziptrek-queenstown":           ("adrenaline-thrills", "zip-lining"),
    "nz-paraglide-queenstown":         ("adrenaline-thrills", "paragliding"),
    "nz-paraglide-wanaka":             ("adrenaline-thrills", "paragliding"),
    "nz-zorb-rotorua":                 ("adrenaline-thrills", "zorbing"),
    "nz-whitewater-rafting-kaituna":   ("adrenaline-thrills", "white-water-rafting"),
    "nz-hot-air-balloon-canterbury":   ("adrenaline-thrills", "hot-air-balloon"),
    "nz-horse-riding-glenorchy":       ("adrenaline-thrills", "horse-riding"),
    "nz-horse-riding-pakiri-beach":    ("adrenaline-thrills", "horse-riding"),
    "nz-horse-riding-tekapo":          ("adrenaline-thrills", "horse-riding"),

    # ── Nature ───────────────────────────────────────────────────────────
    "nz-tama-lakes-track":             ("mountains-hiking", "day-hike"),
    "nz-meads-wall":                   ("culture-history", "film-location"),
    "nz-taranaki-falls":               ("nature-wildlife", "waterfall-walk"),
    "nz-pouakai-tarn":                 ("mountains-hiking", "day-hike"),
    "nz-three-sisters-taranaki":       ("photography-scenery", "scenic-viewpoint"),
    "nz-blue-spring-te-waihou":        ("nature-wildlife", "scenic-walk"),
    "nz-aratiatia-rapids":             ("nature-wildlife", "scenic-walk"),
    "nz-bridal-veil-falls":            ("nature-wildlife", "waterfall-walk"),
    "nz-kaiate-falls":                 ("nature-wildlife", "waterfall-walk"),
    "nz-thunder-creek-falls":          ("nature-wildlife", "waterfall-walk"),
    "nz-blue-pools-track":             ("nature-wildlife", "scenic-walk"),
    "nz-lake-matheson":                ("photography-scenery", "landscape-photography"),
    "nz-devils-punchbowl-waterfall":   ("nature-wildlife", "waterfall-walk"),
    "nz-redwoods-treewalk-rotorua":    ("nature-wildlife", "scenic-walk"),
    "nz-hokitika-gorge":               ("nature-wildlife", "scenic-walk"),
    "nz-glow-worm-dell-hokitika":      ("nature-wildlife", "glowworm-caves"),
    "nz-key-summit-track":             ("mountains-hiking", "day-hike"),
    "nz-lake-marian-track":            ("mountains-hiking", "day-hike"),
    "nz-crown-range-road":             ("photography-scenery", "scenic-drive"),
    "nz-mangapohue-natural-bridge":    ("nature-wildlife", "scenic-walk"),

    # ── Thermal ──────────────────────────────────────────────────────────
    "nz-polynesian-spa-rotorua":       ("hot-springs-relaxation", "spa-experience"),
    "nz-onsen-hot-pools-queenstown":   ("hot-springs-relaxation", "spa-experience"),
    "nz-tekapo-springs":               ("hot-springs-relaxation", "thermal-pool"),
    "nz-lost-spring-whitianga":        ("hot-springs-relaxation", "spa-experience"),
    "nz-wairakei-terraces-taupo":      ("hot-springs-relaxation", "thermal-pool"),
    "nz-hells-gate-rotorua":           ("volcanoes-geothermal", "mud-pools"),
    "nz-spa-thermal-park-taupo":       ("hot-springs-relaxation", "natural-hot-springs"),
    "nz-craters-of-the-moon-taupo":    ("volcanoes-geothermal", "geothermal-park"),
    "nz-kuirau-park-rotorua":          ("volcanoes-geothermal", "geothermal-park"),

    # ── Cultural ─────────────────────────────────────────────────────────
    "nz-waiheke-island-wine-tours":    ("food-wine", "vineyard-tour"),
    "nz-marlborough-wine-tours":       ("food-wine", "vineyard-tour"),
    "nz-central-otago-wine-tours":     ("food-wine", "vineyard-tour"),
    "nz-auckland-food-tour":           ("food-wine", "food-market"),
    "nz-spellbound-glowworm-waitomo":  ("nature-wildlife", "glowworm-caves"),
    "nz-hobbiton-evening-banquet":     ("culture-history", "film-location"),
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
    """Add category/activity after types line and normalize location_name.
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
        if f'"category": "{category}"' in content:
            idx = content.index(slug_pattern)
            nearby = content[max(0, idx-50):idx+200]
            if category in nearby:
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
        print(f"  {f.name}: {n} attractions tagged")
        total += n

    print(f"\nTotal: {total} attractions tagged")

    expected = len(SLUG_TAGS)
    if total != expected:
        print(f"WARNING: expected {expected}, got {total}")
        all_slugs_in_data = set()
        for f in files:
            text = f.read_text()
            for slug in SLUG_TAGS:
                if f'"slug": "{slug}"' in text:
                    all_slugs_in_data.add(slug)
        missing = set(SLUG_TAGS.keys()) - all_slugs_in_data
        if missing:
            print(f"Missing slugs in data files: {missing}")
        sys.exit(1)

    print("Validating tags against taxonomy...")
    sys.path.insert(0, str(data_dir.parent.parent))
    from app.data.activity_taxonomy import validate_attraction_tags
    errors = []
    for slug, (cat, act) in SLUG_TAGS.items():
        errs = validate_attraction_tags(cat, act)
        if errs:
            errors.append(f"  {slug}: {errs}")
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(e)
        sys.exit(1)

    print("All tags valid!")


if __name__ == "__main__":
    main()
