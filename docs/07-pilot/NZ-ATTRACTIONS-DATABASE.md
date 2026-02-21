# NZ Attractions Database — Schema & Seed Data

## Overview

This document defines the complete attractions database schema for the NZ pilot and provides 18 fully populated seed entries. These entries cover a diverse mix of activity types (wildlife, hiking, scenic, water sports, geothermal, cultural) across both islands and serve as the foundation for the MVP database.

The schema aligns with the `attractions` table defined in [DATA-MODEL.md](../05-architecture/DATA-MODEL.md) and the condition profiling system defined in [CONDITION-MONITORING.md](../02-product/CONDITION-MONITORING.md).

---

## Schema Definition

### attractions table (PostgreSQL + PostGIS)

```sql
CREATE TABLE attractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destination VARCHAR(100) NOT NULL,           -- "new-zealand"
    region VARCHAR(100),                          -- "canterbury", "west-coast", "otago", etc.
    name VARCHAR(255) NOT NULL,                   -- Human-readable name
    slug VARCHAR(255) UNIQUE NOT NULL,            -- URL-safe identifier
    description TEXT,                              -- What it is and why it's special
    types TEXT[] NOT NULL,                         -- ["hiking", "scenic", "wildlife"]
    location_name VARCHAR(255),                   -- Nearest town or landmark
    location_point GEOGRAPHY(Point, 4326),        -- PostGIS point (lon, lat)
    difficulty VARCHAR(20),                        -- "easy", "moderate", "hard", "extreme"
    cost_level VARCHAR(20),                        -- "free", "budget", "moderate", "premium"
    duration_min DECIMAL(4,2),                     -- Minimum hours
    duration_max DECIMAL(4,2),                     -- Maximum hours
    seasonal_availability VARCHAR(50) DEFAULT 'year-round',
    booking_required BOOLEAN DEFAULT false,
    weather_sensitivity VARCHAR(20) DEFAULT 'moderate',  -- "low", "moderate", "high", "very-high"
    ideal_conditions JSONB DEFAULT '{}'::jsonb,
    acceptable_conditions JSONB DEFAULT '{}'::jsonb,
    dealbreaker_conditions JSONB DEFAULT '{}'::jsonb,
    logistics JSONB DEFAULT '{}'::jsonb,
    pro_tips JSONB DEFAULT '[]'::jsonb,
    uniqueness_score INTEGER DEFAULT 50,           -- 0-100: how unique/unmissable
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### JSONB Field Schemas

#### ideal_conditions / acceptable_conditions

```json
{
  "temperature_min": 10,
  "temperature_max": 25,
  "wind_speed_max": 20,
  "precipitation_probability_max": 10,
  "cloud_cover_max": 30,
  "visibility_min": 20,
  "wave_height_max": null,
  "uv_index_max": null
}
```

#### dealbreaker_conditions

```json
{
  "wind_speed_above": 60,
  "precipitation_probability_above": null,
  "visibility_below": 1,
  "temperature_below": -5,
  "wave_height_above": null,
  "volcanic_alert_above": null,
  "trail_closed": true,
  "road_closed": true
}
```

#### logistics

```json
{
  "access": "How to reach the attraction",
  "parking": "Parking info",
  "facilities": ["toilets", "shelter", "cafe"],
  "cell_coverage": "good | patchy | none",
  "nearest_fuel": "Town name and distance",
  "nearest_medical": "Hospital or medical center",
  "estimated_cost_nzd": { "adult": 0, "child": 0, "notes": "" },
  "booking_url": "https://...",
  "best_time_of_day": "morning | midday | afternoon | evening | any"
}
```

#### pro_tips

```json
[
  {
    "category": "timing | viewpoint | preparation | hidden_gem | photography | food | logistics | safety",
    "tip": "The tip text",
    "conditions_dependent": false,
    "condition_context": null
  }
]
```

---

## Seed Data — 18 Fully Populated Attractions

### 1. Milford Sound / Piopiotahi Cruise

```json
{
  "destination": "new-zealand",
  "region": "southland-fiordland",
  "name": "Milford Sound / Piopiotahi Cruise",
  "slug": "nz-milford-sound-cruise",
  "description": "A cruise through New Zealand's most famous fiord — 16 km of sheer cliff faces, cascading waterfalls, and dense rainforest. Carved by glaciers over millions of years, Milford Sound is often called the 'eighth wonder of the world'. One of the wettest inhabited places on Earth (~6,800 mm/year), it is spectacular in both clear and rainy conditions.",
  "types": ["scenic", "cruise", "wildlife"],
  "location_name": "Milford Sound",
  "location_point": "SRID=4326;POINT(167.9264 -44.6714)",
  "difficulty": "easy",
  "cost_level": "moderate",
  "duration_min": 2.0,
  "duration_max": 3.0,
  "seasonal_availability": "year-round",
  "booking_required": true,
  "weather_sensitivity": "moderate",
  "ideal_conditions": {
    "temperature_min": 8,
    "temperature_max": 22,
    "wind_speed_max": 30,
    "precipitation_probability_max": 20,
    "cloud_cover_max": 40,
    "visibility_min": 10
  },
  "acceptable_conditions": {
    "temperature_min": 2,
    "temperature_max": 28,
    "wind_speed_max": 50,
    "precipitation_probability_max": 100,
    "cloud_cover_max": 100,
    "visibility_min": 2
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 80,
    "visibility_below": 0.5,
    "road_closed": true
  },
  "logistics": {
    "access": "Drive from Te Anau via SH94 (2 hours). Homer Tunnel is single-lane with traffic lights — expect queues in peak season. Alternatively, take a scenic flight or bus tour from Queenstown.",
    "parking": "Large car park at Milford Sound terminal. Free. Can fill up by 10 AM in peak season.",
    "facilities": ["toilets", "cafe", "visitor_center", "shelter"],
    "cell_coverage": "none",
    "nearest_fuel": "Te Anau (120 km). No fuel at Milford Sound.",
    "nearest_medical": "Te Anau Medical Centre (120 km)",
    "estimated_cost_nzd": { "adult": 85, "child": 25, "notes": "Standard 2-hour cruise. Premium/nature cruises $120-180." },
    "booking_url": "https://www.realjourneys.co.nz/milford-sound",
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "hidden_gem",
      "tip": "Rainy days create hundreds of temporary waterfalls that cascade down the cliff faces — some photographers specifically choose rainy days for the most dramatic imagery. Don't cancel your trip because of rain.",
      "conditions_dependent": true,
      "condition_context": "during or after rain"
    },
    {
      "category": "timing",
      "tip": "The first cruise of the day (usually 8:30-9 AM departure) has the calmest water for reflections and fewest other boats. Worth the early drive from Te Anau (leave by 6:30 AM).",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "logistics",
      "tip": "The drive from Te Anau is stunning in its own right — budget time for photo stops at Mirror Lakes, the Avenue of the Disappearing Mountain, and the Chasm walk (10 min, excellent).",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "preparation",
      "tip": "Sandflies at the terminal and foreshore are legendary. Apply insect repellent before getting out of the car. Once on the boat, they're not a problem.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "photography",
      "tip": "On clear mornings, Mitre Peak reflects perfectly in the still water near the terminal — photograph this BEFORE boarding your cruise, not after.",
      "conditions_dependent": true,
      "condition_context": "calm, clear mornings"
    }
  ],
  "uniqueness_score": 95,
  "metadata": {
    "island": "south",
    "national_park": "fiordland",
    "world_heritage": true,
    "rainy_day_alternative": true
  }
}
```

### 2. Tongariro Alpine Crossing

```json
{
  "destination": "new-zealand",
  "region": "tongariro-central-plateau",
  "name": "Tongariro Alpine Crossing",
  "slug": "nz-tongariro-alpine-crossing",
  "description": "New Zealand's most famous day hike — a 19.4 km one-way traverse through an active volcanic landscape. Passing through craters, across lava flows, past emerald-colored lakes, and over exposed ridges between Mt Tongariro and Mt Ngāuruhoe (Mt Doom in Lord of the Rings). Stunning but extremely weather-sensitive.",
  "types": ["hiking", "scenic", "volcanic"],
  "location_name": "Tongariro National Park",
  "location_point": "SRID=4326;POINT(175.6523 -39.1328)",
  "difficulty": "hard",
  "cost_level": "budget",
  "duration_min": 6.0,
  "duration_max": 8.0,
  "seasonal_availability": "oct-apr (summer mode), jun-sep (winter alpine — experienced only)",
  "booking_required": false,
  "weather_sensitivity": "very-high",
  "ideal_conditions": {
    "temperature_min": 10,
    "temperature_max": 22,
    "wind_speed_max": 25,
    "precipitation_probability_max": 10,
    "cloud_cover_max": 20,
    "visibility_min": 30
  },
  "acceptable_conditions": {
    "temperature_min": 5,
    "temperature_max": 28,
    "wind_speed_max": 40,
    "precipitation_probability_max": 30,
    "cloud_cover_max": 50,
    "visibility_min": 10
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 50,
    "visibility_below": 1,
    "temperature_below": -5,
    "volcanic_alert_above": 2,
    "trail_closed": true
  },
  "logistics": {
    "access": "One-way hike requires shuttle bus. Mangatepopo car park (start) to Ketetahi car park (finish). Multiple shuttle operators from National Park Village, Tūrangi, and Ōhakune.",
    "parking": "Shuttle operators handle parking. Do not leave car at Mangatepopo (one-way hike).",
    "facilities": ["toilets_at_trailheads", "emergency_shelter_on_track"],
    "cell_coverage": "none on the track",
    "nearest_fuel": "National Park Village (15 km), Tūrangi (45 km)",
    "nearest_medical": "Taumarunui Hospital (55 km), Taupō Hospital (100 km)",
    "estimated_cost_nzd": { "adult": 45, "child": 25, "notes": "Shuttle bus cost. Track itself is free." },
    "booking_url": "https://www.tongarirocrossing.org.nz",
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "viewpoint",
      "tip": "The best photo of the Emerald Lakes is from the ridge about 50 metres BEFORE the official viewpoint — you get all three lakes with Red Crater rising behind them. Most people walk right past this spot.",
      "conditions_dependent": true,
      "condition_context": "clear skies"
    },
    {
      "category": "safety",
      "tip": "The section between Red Crater and Ketetahi is exposed to fierce winds. Even on a calm day in the car park, summit winds can be 3-4x stronger. Carry warm layers and a wind shell no matter what.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "timing",
      "tip": "Start early (6-7 AM shuttle). By mid-morning, hundreds of hikers create bottlenecks at narrow sections. Early starters get the volcanic landscapes to themselves and avoid afternoon weather deterioration.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "preparation",
      "tip": "Carry minimum 2 litres of water — there are no water sources on the main track. Volcanic terrain is dehydrating. In summer heat, carry 3 litres.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 95,
  "metadata": {
    "island": "north",
    "national_park": "tongariro",
    "world_heritage": true,
    "lord_of_the_rings": true,
    "shuttle_required": true
  }
}
```

### 3. Franz Josef Glacier Heli-Hike

```json
{
  "destination": "new-zealand",
  "region": "west-coast",
  "name": "Franz Josef Glacier Heli-Hike",
  "slug": "nz-franz-josef-glacier-heli-hike",
  "description": "A helicopter flight onto Franz Josef Glacier followed by a guided walk through stunning blue ice caves, crevasses, and ice formations. One of the world's most accessible glacier experiences — descending through temperate rainforest almost to sea level. Extremely weather-dependent due to helicopter requirements.",
  "types": ["glacier", "hiking", "adventure", "scenic"],
  "location_name": "Franz Josef",
  "location_point": "SRID=4326;POINT(170.1834 -43.3862)",
  "difficulty": "moderate",
  "cost_level": "premium",
  "duration_min": 3.0,
  "duration_max": 4.0,
  "seasonal_availability": "year-round (weather permitting)",
  "booking_required": true,
  "weather_sensitivity": "very-high",
  "ideal_conditions": {
    "temperature_min": 5,
    "temperature_max": 20,
    "wind_speed_max": 15,
    "precipitation_probability_max": 10,
    "cloud_cover_max": 30,
    "visibility_min": 20
  },
  "acceptable_conditions": {
    "temperature_min": 0,
    "temperature_max": 25,
    "wind_speed_max": 25,
    "precipitation_probability_max": 20,
    "cloud_cover_max": 50,
    "visibility_min": 10
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 35,
    "precipitation_probability_above": 60,
    "visibility_below": 3,
    "cloud_cover_above": 80
  },
  "logistics": {
    "access": "Franz Josef village, Main Road. Check in at operator's shop 30 min before flight.",
    "parking": "Village parking, free. Walk to operators.",
    "facilities": ["toilets", "cafe", "gear_hire_included"],
    "cell_coverage": "good in village, none on glacier",
    "nearest_fuel": "Franz Josef village",
    "nearest_medical": "Franz Josef Medical Centre (in village)",
    "estimated_cost_nzd": { "adult": 499, "child": 399, "notes": "Includes helicopter, boots, crampons, waterproof jacket, guide. Advance booking essential in peak season." },
    "booking_url": "https://www.franzjosefglacier.com",
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "logistics",
      "tip": "Book for your first available day in the area and ask about their rescheduling policy — most operators will rebook to the next clear day for free if weather cancels. Plan 2 days in the glacier area to maximize your chances.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "timing",
      "tip": "Morning flights are more likely to operate — cloud tends to build through the afternoon. Request the earliest available slot.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "preparation",
      "tip": "Even on sunny days, the glacier is cold. Wear long pants and layers. All technical gear (boots, crampons, jacket) is provided by the operator.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "hidden_gem",
      "tip": "If the heli-hike cancels, the free Roberts Point Track (5 hrs return, hard) gives an incredible elevated view of the glacier. Or try the gentler Franz Josef Glacier Valley Walk (1.5 hrs return) to the glacier terminal viewpoint.",
      "conditions_dependent": true,
      "condition_context": "when heli-hike is cancelled due to weather"
    }
  ],
  "uniqueness_score": 90,
  "metadata": {
    "island": "south",
    "cancellation_rate_percent": 35,
    "helicopter_required": true,
    "all_weather_alternative": "franz-josef-valley-walk"
  }
}
```

### 4. Kaikōura Whale Watching

```json
{
  "destination": "new-zealand",
  "region": "marlborough",
  "name": "Kaikōura Whale Watching",
  "slug": "nz-kaikoura-whale-watching",
  "description": "Watch giant sperm whales in their natural habitat just minutes from shore. Kaikōura's unique underwater canyon drops to 1,000+ m depth close to the coast, creating a nutrient-rich environment that supports resident sperm whales, dusky dolphins, NZ fur seals, and occasional orcas and blue whales.",
  "types": ["wildlife", "cruise", "marine"],
  "location_name": "Kaikōura",
  "location_point": "SRID=4326;POINT(173.6800 -42.4006)",
  "difficulty": "easy",
  "cost_level": "premium",
  "duration_min": 2.5,
  "duration_max": 3.5,
  "seasonal_availability": "year-round",
  "booking_required": true,
  "weather_sensitivity": "very-high",
  "ideal_conditions": {
    "temperature_min": 8,
    "temperature_max": 25,
    "wind_speed_max": 15,
    "precipitation_probability_max": 20,
    "wave_height_max": 1.0,
    "visibility_min": 10
  },
  "acceptable_conditions": {
    "temperature_min": 2,
    "temperature_max": 30,
    "wind_speed_max": 30,
    "precipitation_probability_max": 50,
    "wave_height_max": 2.0,
    "visibility_min": 5
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 40,
    "wave_height_above": 3.0
  },
  "logistics": {
    "access": "Whale Watch Kaikōura office, Railway Station, Whaleway Station Road, central Kaikōura.",
    "parking": "Free parking at the railway station site.",
    "facilities": ["toilets", "cafe", "gift_shop", "shelter"],
    "cell_coverage": "good in town, patchy at sea",
    "nearest_fuel": "Kaikōura township",
    "nearest_medical": "Kaikōura Health Centre",
    "estimated_cost_nzd": { "adult": 165, "child": 60, "notes": "80% refund if no whales sighted (rare — success rate >95%). Book well ahead in summer." },
    "booking_url": "https://www.whalewatch.co.nz",
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "Early morning tours have the calmest seas and best light for photography. The 7:15 AM departure is the most popular with photographers.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "preparation",
      "tip": "Take seasickness medication 30 minutes before boarding even if you don't normally get motion sick. The swells off Kaikōura can be significant. Ginger tablets or prescription patches work best.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "photography",
      "tip": "Sperm whales surface for 8-10 minutes between dives. The iconic tail fluke shot happens just as they dive — keep your camera ready during the entire surface time. The crew will call out 'diving' moments before.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "hidden_gem",
      "tip": "After the whale watch, drive 20 minutes north to Ōhau Stream Waterfall Walk (10 min flat walk) to see NZ fur seal pups playing in rock pools — November to February is best. Free, uncrowded, and magical.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 92,
  "metadata": {
    "island": "south",
    "sighting_success_rate_percent": 95,
    "species": ["sperm_whale", "dusky_dolphin", "nz_fur_seal", "hectors_dolphin", "orca"]
  }
}
```

### 5. Abel Tasman Coast Track (Day Walk + Kayak)

```json
{
  "destination": "new-zealand",
  "region": "nelson-tasman",
  "name": "Abel Tasman Coast Track — Day Walk & Kayak",
  "slug": "nz-abel-tasman-day",
  "description": "Golden sand beaches, turquoise water, and lush coastal bush in New Zealand's smallest and most accessible national park. The Coast Track can be experienced as a full Great Walk (3-5 days) or as flexible day sections via water taxi and kayak — the most popular day option combines a water taxi with a coastal walk and optional kayaking.",
  "types": ["hiking", "kayaking", "beach", "scenic", "great-walk"],
  "location_name": "Marahau / Kaiteriteri",
  "location_point": "SRID=4326;POINT(173.0150 -40.9750)",
  "difficulty": "easy-moderate",
  "cost_level": "moderate",
  "duration_min": 4.0,
  "duration_max": 8.0,
  "seasonal_availability": "year-round (track); kayak best oct-apr",
  "booking_required": true,
  "weather_sensitivity": "moderate",
  "ideal_conditions": {
    "temperature_min": 15,
    "temperature_max": 28,
    "wind_speed_max": 15,
    "precipitation_probability_max": 10,
    "cloud_cover_max": 30,
    "wave_height_max": 0.5
  },
  "acceptable_conditions": {
    "temperature_min": 8,
    "temperature_max": 30,
    "wind_speed_max": 30,
    "precipitation_probability_max": 40,
    "cloud_cover_max": 70,
    "wave_height_max": 1.0
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 40,
    "wave_height_above": 2.0
  },
  "logistics": {
    "access": "Marahau (road end, water taxi departure) is 68 km / 1 hr from Nelson. Kaiteriteri is nearby and also has water taxi services.",
    "parking": "Paid parking at Marahau (~$10 NZD/day) and Kaiteriteri.",
    "facilities": ["toilets_at_trailhead", "cafe_marahau", "kayak_hire"],
    "cell_coverage": "patchy along the track, good in Marahau/Kaiteriteri",
    "nearest_fuel": "Motueka (18 km from Marahau)",
    "nearest_medical": "Motueka Medical Centre (18 km)",
    "estimated_cost_nzd": { "adult": 80, "child": 45, "notes": "Water taxi. Guided kayak day trip: $180-250. Combined walk+kayak: $150-220." },
    "booking_url": "https://www.abeltasman.co.nz",
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "logistics",
      "tip": "The most rewarding day combo: water taxi to Bark Bay (45 min ride), walk south to Torrent Bay (2 hrs, easy), then water taxi back. You get golden beaches, coastal forest, and a swing bridge without an exhausting full-day walk.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "timing",
      "tip": "Visit Tonga Island (NZ fur seal colony) via kayak in the morning — seals are most active and the sea is typically calmer before the afternoon sea breeze kicks in.",
      "conditions_dependent": true,
      "condition_context": "calm morning conditions"
    },
    {
      "category": "hidden_gem",
      "tip": "Cleopatra's Pool — a natural rock waterslide and swimming hole a short detour off the main track near Torrent Bay. Locals love it. Most tourists walk right past the turnoff.",
      "conditions_dependent": true,
      "condition_context": "warm weather for swimming"
    }
  ],
  "uniqueness_score": 85,
  "metadata": {
    "island": "south",
    "national_park": "abel-tasman",
    "great_walk": true,
    "water_taxi_required_for_day_trips": true
  }
}
```

### 6. Lake Tekapo Stargazing (Dark Sky Reserve)

```json
{
  "destination": "new-zealand",
  "region": "canterbury",
  "name": "Lake Tekapo / Aoraki Mackenzie Dark Sky Reserve",
  "slug": "nz-lake-tekapo-stargazing",
  "description": "The Aoraki Mackenzie International Dark Sky Reserve is the world's largest dark sky reserve — and Lake Tekapo is its gateway. On clear nights, the Milky Way is visible with the naked eye in extraordinary detail. Mt John Observatory offers guided stargazing tours with powerful telescopes. The turquoise glacial lake is stunning by day too.",
  "types": ["stargazing", "scenic", "astronomy"],
  "location_name": "Lake Tekapo / Takapō",
  "location_point": "SRID=4326;POINT(170.4772 -44.0047)",
  "difficulty": "easy",
  "cost_level": "moderate",
  "duration_min": 2.0,
  "duration_max": 3.0,
  "seasonal_availability": "year-round (best apr-sep for longer dark hours)",
  "booking_required": true,
  "weather_sensitivity": "very-high",
  "ideal_conditions": {
    "temperature_min": -5,
    "temperature_max": 20,
    "wind_speed_max": 15,
    "precipitation_probability_max": 5,
    "cloud_cover_max": 10,
    "visibility_min": 50
  },
  "acceptable_conditions": {
    "temperature_min": -10,
    "temperature_max": 25,
    "wind_speed_max": 25,
    "precipitation_probability_max": 15,
    "cloud_cover_max": 30,
    "visibility_min": 20
  },
  "dealbreaker_conditions": {
    "cloud_cover_above": 60,
    "precipitation_probability_above": 50,
    "wind_speed_above": 40
  },
  "logistics": {
    "access": "Lake Tekapo township, SH8 between Christchurch and Mt Cook. Mt John Observatory is 5 min drive from town.",
    "parking": "Town centre parking free. Mt John has limited parking (tour shuttle recommended).",
    "facilities": ["toilets", "cafe_daytime", "observatory"],
    "cell_coverage": "good in town",
    "nearest_fuel": "Lake Tekapo village",
    "nearest_medical": "Twizel Medical Centre (55 km) or Timaru Hospital (105 km)",
    "estimated_cost_nzd": { "adult": 135, "child": 75, "notes": "Dark Sky Experience guided tour. Daytime Mt John walk is free." },
    "booking_url": "https://www.darkskyproject.co.nz",
    "best_time_of_day": "evening"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "Check the moon phase before booking. A full moon washes out the Milky Way and most deep-sky objects. New moon ±5 days gives the darkest skies.",
      "conditions_dependent": true,
      "condition_context": "new moon phase"
    },
    {
      "category": "photography",
      "tip": "The Church of the Good Shepherd is iconic at night with the Milky Way behind it — but during the tour you're at Mt John. For church night photos, go independently (free) on a separate clear night. Tripod essential, 15-25 second exposure.",
      "conditions_dependent": true,
      "condition_context": "clear, moonless night"
    },
    {
      "category": "preparation",
      "tip": "It gets extremely cold at night, even in summer (can drop to 5°C in January). In winter, temperatures of -10°C are possible. Bring your warmest layers, hat, and gloves for the stargazing tour.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 88,
  "metadata": {
    "island": "south",
    "dark_sky_reserve": true,
    "aurora_possible": true,
    "moon_phase_critical": true,
    "daytime_activity": "mt-john-walk"
  }
}
```

### 7. Hooker Valley Track

```json
{
  "destination": "new-zealand",
  "region": "canterbury",
  "name": "Hooker Valley Track",
  "slug": "nz-hooker-valley-track",
  "description": "A stunning valley walk to the glacier-fed Hooker Lake with Aoraki/Mt Cook towering above. Three swing bridges cross braided rivers, and the final lake view — icebergs floating beneath NZ's highest peak — is one of the most photographed scenes in the country. Arguably the best effort-to-reward ratio of any walk in NZ.",
  "types": ["hiking", "scenic", "alpine"],
  "location_name": "Aoraki/Mt Cook Village",
  "location_point": "SRID=4326;POINT(170.0944 -43.7167)",
  "difficulty": "easy",
  "cost_level": "free",
  "duration_min": 2.5,
  "duration_max": 4.0,
  "seasonal_availability": "year-round (can be icy in winter)",
  "booking_required": false,
  "weather_sensitivity": "high",
  "ideal_conditions": {
    "temperature_min": 8,
    "temperature_max": 22,
    "wind_speed_max": 20,
    "precipitation_probability_max": 10,
    "cloud_cover_max": 20,
    "visibility_min": 30
  },
  "acceptable_conditions": {
    "temperature_min": 0,
    "temperature_max": 28,
    "wind_speed_max": 40,
    "precipitation_probability_max": 40,
    "cloud_cover_max": 60,
    "visibility_min": 5
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 60,
    "visibility_below": 1,
    "trail_closed": true
  },
  "logistics": {
    "access": "White Horse Hill car park, end of Hooker Valley Road, Aoraki/Mt Cook Village.",
    "parking": "Free. Can fill by 9 AM in peak summer. Arrive early.",
    "facilities": ["toilets_at_trailhead", "shelter"],
    "cell_coverage": "patchy",
    "nearest_fuel": "Twizel (55 km)",
    "nearest_medical": "Twizel Medical Centre (55 km)",
    "estimated_cost_nzd": { "adult": 0, "child": 0, "notes": "Free. No booking required." },
    "booking_url": null,
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "Mt Cook is only clearly visible about 30% of the time. If you arrive at your accommodation and the mountain is out, consider doing the walk immediately rather than waiting for 'tomorrow' — the weather might not hold.",
      "conditions_dependent": true,
      "condition_context": "clear sky with Mt Cook visible"
    },
    {
      "category": "viewpoint",
      "tip": "The second swing bridge has the best view of Mt Cook framed by the valley. Most people rush past it heading to the lake. Stop here on the way out when the light is often better (afternoon sun on Mt Cook from this angle).",
      "conditions_dependent": true,
      "condition_context": "clear afternoon"
    },
    {
      "category": "photography",
      "tip": "At the glacier lake, walk right along the shoreline to the left side for the best angle of icebergs with Mt Cook behind. The main viewpoint platform is good but the shore gives better foreground interest.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "logistics",
      "tip": "If you're spending the night at Mt Cook Village or Glentanner, check conditions for both the Hooker Valley Track and the Tasman Glacier Lake boat tour — they have different weather sensitivities and one may work when the other doesn't.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 90,
  "metadata": {
    "island": "south",
    "national_park": "aoraki-mt-cook",
    "mt_cook_visible_percent": 30,
    "swing_bridges": 3,
    "wheelchair_accessible_to": "first_bridge"
  }
}
```

### 8. Rotorua Geothermal — Wai-O-Tapu

```json
{
  "destination": "new-zealand",
  "region": "rotorua",
  "name": "Wai-O-Tapu Thermal Wonderland",
  "slug": "nz-wai-o-tapu",
  "description": "The most colorful geothermal area in NZ — vivid greens, oranges, and blues created by mineral deposits in volcanic craters and hot springs. Features include the Champagne Pool (74°C, orange-rimmed), Devil's Bath (vivid chartreuse), and the Lady Knox Geyser (triggered daily at 10:15 AM). A boardwalk loop through an alien landscape.",
  "types": ["geothermal", "scenic", "volcanic"],
  "location_name": "Rotorua",
  "location_point": "SRID=4326;POINT(176.3657 -38.3553)",
  "difficulty": "easy",
  "cost_level": "moderate",
  "duration_min": 1.5,
  "duration_max": 2.5,
  "seasonal_availability": "year-round",
  "booking_required": false,
  "weather_sensitivity": "low",
  "ideal_conditions": {
    "temperature_min": 5,
    "temperature_max": 25,
    "wind_speed_max": 30,
    "precipitation_probability_max": 30,
    "cloud_cover_max": 60
  },
  "acceptable_conditions": {
    "temperature_min": -5,
    "temperature_max": 35,
    "wind_speed_max": 60,
    "precipitation_probability_max": 80,
    "cloud_cover_max": 100
  },
  "dealbreaker_conditions": {
    "volcanic_alert_above": 3
  },
  "logistics": {
    "access": "201 Waiotapu Loop Road, 27 km south of Rotorua on SH5. Well signposted.",
    "parking": "Large free car park at the entrance.",
    "facilities": ["toilets", "cafe", "gift_shop"],
    "cell_coverage": "good",
    "nearest_fuel": "Rotorua (27 km) or Wai-O-Tapu Store (2 km)",
    "nearest_medical": "Rotorua Hospital (27 km)",
    "estimated_cost_nzd": { "adult": 50, "child": 18, "notes": "Online discount often available. Lady Knox Geyser is a separate area — drive there for the 10:15 AM show, then return to the main park." },
    "booking_url": "https://www.waiotapu.co.nz",
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "Arrive at the Lady Knox Geyser area by 10:00 AM for the 10:15 eruption. After the show, drive to the main thermal park (5 min). Starting the boardwalk loop by 10:45 AM means you beat the tour bus crowds.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "photography",
      "tip": "Overcast days produce better photos of the thermal features — no harsh shadows, and the colors are more saturated. Steam is also more visible against grey sky than blue sky.",
      "conditions_dependent": true,
      "condition_context": "overcast conditions"
    },
    {
      "category": "hidden_gem",
      "tip": "The Mud Pool (free, roadside, 1 km from the entrance) is actually more impressive than many features inside the park — massive boiling mud bubbles. Don't skip it.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 82,
  "metadata": {
    "island": "north",
    "all_weather": true,
    "lady_knox_geyser_time": "10:15",
    "rainy_day_alternative": true
  }
}
```

### 9. Waitomo Glowworm Caves

```json
{
  "destination": "new-zealand",
  "region": "waikato",
  "name": "Waitomo Glowworm Caves",
  "slug": "nz-waitomo-glowworm-caves",
  "description": "Millions of tiny glowworms (Arachnocampa luminosa) create a bioluminescent 'galaxy' on the ceiling of ancient limestone caves. A silent boat ride through the main grotto, beneath thousands of pinpricks of blue-green light, is one of NZ's most magical experiences. Completely underground and weather-independent.",
  "types": ["nature", "cave", "scenic"],
  "location_name": "Waitomo",
  "location_point": "SRID=4326;POINT(175.1060 -38.2610)",
  "difficulty": "easy",
  "cost_level": "moderate",
  "duration_min": 0.75,
  "duration_max": 1.5,
  "seasonal_availability": "year-round",
  "booking_required": true,
  "weather_sensitivity": "low",
  "ideal_conditions": {
    "temperature_min": -10,
    "temperature_max": 40,
    "wind_speed_max": 100,
    "precipitation_probability_max": 100,
    "cloud_cover_max": 100
  },
  "acceptable_conditions": {
    "temperature_min": -10,
    "temperature_max": 40,
    "wind_speed_max": 100,
    "precipitation_probability_max": 100,
    "cloud_cover_max": 100
  },
  "dealbreaker_conditions": {
    "road_closed": true
  },
  "logistics": {
    "access": "39 Waitomo Village Road, Waitomo. 2.5 hours south of Auckland, 1 hour west of Rotorua.",
    "parking": "Free at the visitor centre.",
    "facilities": ["toilets", "cafe", "gift_shop", "visitor_centre"],
    "cell_coverage": "good in the village",
    "nearest_fuel": "Ōtorohanga (16 km)",
    "nearest_medical": "Ōtorohanga Medical Centre (16 km)",
    "estimated_cost_nzd": { "adult": 55, "child": 25, "notes": "Glowworm Cave tour. Combo with Ruakuri Cave: $85. Black Water Rafting (separate company): $155-260." },
    "booking_url": "https://www.waitomo.com",
    "best_time_of_day": "any"
  },
  "pro_tips": [
    {
      "category": "logistics",
      "tip": "Waitomo and Hobbiton can be combined in one day — they're about 1.5 hours apart. Do the morning Hobbiton tour (10:30 AM), then drive to Waitomo for an afternoon cave tour (2:30-3 PM).",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "hidden_gem",
      "tip": "For a more immersive experience, try the Ruakuri Cave walking tour instead of (or in addition to) the main Glowworm Cave. It's longer, more dramatic, and far less crowded.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "timing",
      "tip": "The first and last tours of the day have the smallest groups. Mid-morning (10-11 AM) is when the big tour bus groups arrive from Auckland and Rotorua.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 85,
  "metadata": {
    "island": "north",
    "all_weather": true,
    "underground": true,
    "rainy_day_alternative": true,
    "combinable_with": "hobbiton"
  }
}
```

### 10. Hobbiton Movie Set

```json
{
  "destination": "new-zealand",
  "region": "waikato",
  "name": "Hobbiton Movie Set",
  "slug": "nz-hobbiton",
  "description": "The Shire from Peter Jackson's Lord of the Rings and Hobbit trilogies, preserved as a permanent attraction on a working sheep farm near Matamata. 44 hobbit holes, the Green Dragon Inn, the Party Tree, and the meticulously maintained gardens bring Middle-earth to life.",
  "types": ["cultural", "film", "scenic"],
  "location_name": "Matamata",
  "location_point": "SRID=4326;POINT(175.6830 -37.8720)",
  "difficulty": "easy",
  "cost_level": "moderate",
  "duration_min": 2.0,
  "duration_max": 2.5,
  "seasonal_availability": "year-round",
  "booking_required": true,
  "weather_sensitivity": "low",
  "ideal_conditions": {
    "temperature_min": 10,
    "temperature_max": 25,
    "wind_speed_max": 30,
    "precipitation_probability_max": 20,
    "cloud_cover_max": 50
  },
  "acceptable_conditions": {
    "temperature_min": 0,
    "temperature_max": 35,
    "wind_speed_max": 50,
    "precipitation_probability_max": 80,
    "cloud_cover_max": 100
  },
  "dealbreaker_conditions": {
    "road_closed": true
  },
  "logistics": {
    "access": "501 Buckland Road, Matamata. All visitors must check in at the Shire's Rest cafe (tour departure point). Private vehicles drive to the set via shuttle bus from the cafe.",
    "parking": "Free at Shire's Rest.",
    "facilities": ["toilets", "cafe", "gift_shop", "green_dragon_inn"],
    "cell_coverage": "good",
    "nearest_fuel": "Matamata (8 km)",
    "nearest_medical": "Matamata Medical Centre (8 km)",
    "estimated_cost_nzd": { "adult": 89, "child": 44, "notes": "Standard 2-hour guided tour. Afternoon tours include a drink at the Green Dragon Inn. Evening Feast tours available (dinner + tour, $259)." },
    "booking_url": "https://www.hobbitontours.com",
    "best_time_of_day": "afternoon"
  },
  "pro_tips": [
    {
      "category": "photography",
      "tip": "Overcast or lightly drizzly days actually look the most 'Shire-like' — soft green light, no harsh shadows on the hobbit holes, and the gardens look lush. Bright sunny days create contrast that's harder to photograph.",
      "conditions_dependent": true,
      "condition_context": "overcast or light drizzle"
    },
    {
      "category": "timing",
      "tip": "Book the last afternoon tour that includes the Green Dragon Inn drink — smaller group (many day-trippers have left), golden hour light, and you get to linger in the pub.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "logistics",
      "tip": "The tour is exactly 2 hours and heavily structured (guided group). You cannot wander freely. This means timing with other activities is precise — you'll be out exactly when expected.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 80,
  "metadata": {
    "island": "north",
    "lord_of_the_rings": true,
    "all_weather": true,
    "rainy_day_alternative": true,
    "combinable_with": "waitomo-glowworm-caves"
  }
}
```

### 11. Cathedral Cove

```json
{
  "destination": "new-zealand",
  "region": "coromandel",
  "name": "Cathedral Cove / Te Whanganui-A-Hei",
  "slug": "nz-cathedral-cove",
  "description": "An iconic natural rock arch framing a pristine white sand beach on the Coromandel Peninsula. Accessible only on foot (30-45 min walk from the car park) or by boat/kayak, it feels like a hidden paradise. One of NZ's most photographed locations and a filming location for Narnia: Prince Caspian.",
  "types": ["scenic", "beach", "hiking", "coastal"],
  "location_name": "Hahei",
  "location_point": "SRID=4326;POINT(175.7876 -36.8277)",
  "difficulty": "easy-moderate",
  "cost_level": "free",
  "duration_min": 2.0,
  "duration_max": 3.5,
  "seasonal_availability": "year-round (track can close in storms)",
  "booking_required": false,
  "weather_sensitivity": "moderate",
  "ideal_conditions": {
    "temperature_min": 18,
    "temperature_max": 28,
    "wind_speed_max": 20,
    "precipitation_probability_max": 10,
    "cloud_cover_max": 30,
    "wave_height_max": 1.0
  },
  "acceptable_conditions": {
    "temperature_min": 10,
    "temperature_max": 32,
    "wind_speed_max": 35,
    "precipitation_probability_max": 40,
    "cloud_cover_max": 70,
    "wave_height_max": 1.5
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 50,
    "wave_height_above": 2.5,
    "trail_closed": true
  },
  "logistics": {
    "access": "Cathedral Cove car park, Hahei. Peak season (Dec-Feb): park at the park-and-ride lot in Hahei village and take the shuttle ($5 return). Off-peak: drive to the car park directly.",
    "parking": "Limited at the car park ($10/day). Shuttle from Hahei village in peak season.",
    "facilities": ["toilets_at_car_park", "none_at_beach"],
    "cell_coverage": "good in Hahei, patchy on the walk",
    "nearest_fuel": "Whitianga (30 km)",
    "nearest_medical": "Whitianga Medical Centre (30 km)",
    "estimated_cost_nzd": { "adult": 0, "child": 0, "notes": "Free. Shuttle/parking costs only. Kayak tours from Hahei: $120-160." },
    "booking_url": null,
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "Arrive before 8 AM to have the beach almost to yourself. Tour buses and day-trippers start arriving at 9:30 AM and by 10 AM it can be packed with hundreds of people. Early morning light through the arch is also best for photos.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "logistics",
      "tip": "Combine with Hot Water Beach (15 min drive south). Check tide times — Hot Water Beach requires being within 2 hours of low tide. Do Cathedral Cove early morning, then Hot Water Beach at the right tide.",
      "conditions_dependent": true,
      "condition_context": "low tide window"
    },
    {
      "category": "hidden_gem",
      "tip": "Stingray Bay, a small beach you pass on the walk BEFORE Cathedral Cove, is often deserted and has beautiful snorkelling in calm conditions. Most people walk straight past it.",
      "conditions_dependent": true,
      "condition_context": "calm seas, warm weather"
    }
  ],
  "uniqueness_score": 85,
  "metadata": {
    "island": "north",
    "narnia_filming": true,
    "tide_dependent_partially": true,
    "combinable_with": "hot-water-beach"
  }
}
```

### 12. Queenstown Bungy (Kawarau Bridge)

```json
{
  "destination": "new-zealand",
  "region": "otago",
  "name": "Kawarau Bridge Bungy",
  "slug": "nz-kawarau-bungy",
  "description": "The birthplace of commercial bungy jumping — a 43-metre leap from the historic Kawarau Bridge above a turquoise river gorge. AJ Hackett opened the world's first commercial bungy site here in 1988. The bridge jump offers the option of a water-touch (dipping into the river), adding to the thrill.",
  "types": ["adventure", "iconic"],
  "location_name": "Queenstown",
  "location_point": "SRID=4326;POINT(168.8200 -45.0150)",
  "difficulty": "easy",
  "cost_level": "premium",
  "duration_min": 1.0,
  "duration_max": 2.0,
  "seasonal_availability": "year-round",
  "booking_required": true,
  "weather_sensitivity": "low",
  "ideal_conditions": {
    "temperature_min": 5,
    "temperature_max": 30,
    "wind_speed_max": 30,
    "precipitation_probability_max": 30,
    "cloud_cover_max": 60
  },
  "acceptable_conditions": {
    "temperature_min": -5,
    "temperature_max": 35,
    "wind_speed_max": 50,
    "precipitation_probability_max": 70,
    "cloud_cover_max": 100
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 60
  },
  "logistics": {
    "access": "Kawarau Bungy Centre, State Highway 6, 23 minutes from Queenstown towards Cromwell.",
    "parking": "Free at the bungy centre.",
    "facilities": ["toilets", "cafe", "viewing_deck", "gift_shop"],
    "cell_coverage": "good",
    "nearest_fuel": "Frankton/Queenstown (20 km)",
    "nearest_medical": "Lakes District Hospital, Queenstown (23 km)",
    "estimated_cost_nzd": { "adult": 220, "child": 0, "notes": "Min age 10, min weight 35 kg. Photos/video package additional $50-80. Combo deals with Nevis and Ledge bungy available." },
    "booking_url": "https://www.bungy.co.nz",
    "best_time_of_day": "any"
  },
  "pro_tips": [
    {
      "category": "logistics",
      "tip": "If you're doing multiple AJ Hackett activities (Kawarau, Nevis, Ledge), buy the multi-jump combo pass — it saves 20-30% versus individual bookings.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "hidden_gem",
      "tip": "Even non-jumpers should visit — the viewing platform is free and watching others jump is entertaining. The cafe overlooking the gorge is a great coffee stop on the Queenstown-Cromwell drive.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "timing",
      "tip": "Afternoon light (2-4 PM) gives the best photos and video — the sun illuminates the river gorge beautifully. Morning can be shadowed in winter.",
      "conditions_dependent": true,
      "condition_context": "clear afternoon"
    }
  ],
  "uniqueness_score": 78,
  "metadata": {
    "island": "south",
    "all_weather": true,
    "min_age": 10,
    "min_weight_kg": 35,
    "max_weight_kg": 235
  }
}
```

### 13. Otago Peninsula Wildlife

```json
{
  "destination": "new-zealand",
  "region": "otago",
  "name": "Otago Peninsula Wildlife",
  "slug": "nz-otago-peninsula-wildlife",
  "description": "A wildlife wonderland on Dunedin's doorstep. The peninsula hosts the world's only mainland Royal Albatross colony (Taiaroa Head), rare yellow-eyed penguins (hoiho), blue penguin colonies, NZ fur seals, and sea lions. A full day here combines multiple species encounters across the peninsula's dramatic coastal landscape.",
  "types": ["wildlife", "scenic", "nature"],
  "location_name": "Dunedin",
  "location_point": "SRID=4326;POINT(170.6440 -45.8650)",
  "difficulty": "easy",
  "cost_level": "moderate",
  "duration_min": 3.0,
  "duration_max": 6.0,
  "seasonal_availability": "year-round (species vary by season)",
  "booking_required": true,
  "weather_sensitivity": "moderate",
  "ideal_conditions": {
    "temperature_min": 8,
    "temperature_max": 22,
    "wind_speed_max": 40,
    "precipitation_probability_max": 30,
    "cloud_cover_max": 60
  },
  "acceptable_conditions": {
    "temperature_min": 0,
    "temperature_max": 28,
    "wind_speed_max": 60,
    "precipitation_probability_max": 60,
    "cloud_cover_max": 100
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 80
  },
  "logistics": {
    "access": "Royal Albatross Centre at Taiaroa Head — 30 min drive from central Dunedin via Portobello Road along the harbour, or the scenic highcliff road.",
    "parking": "Free at the Albatross Centre and other peninsula viewing points.",
    "facilities": ["toilets", "cafe_at_albatross_centre", "gift_shop"],
    "cell_coverage": "good along the harbour side, patchy on the ocean side",
    "nearest_fuel": "Portobello (10 km) or Dunedin (30 km)",
    "nearest_medical": "Dunedin Hospital (30 km)",
    "estimated_cost_nzd": { "adult": 60, "child": 25, "notes": "Royal Albatross Centre Classic tour. Penguin Place (yellow-eyed penguins): $60. Elm Wildlife Tours (multi-species): $95. Blue penguin viewing (Pilots Beach): $35." },
    "booking_url": "https://albatross.org.nz",
    "best_time_of_day": "afternoon"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "Albatross are best seen in the afternoon when they're actively flying. Paradoxically, they need WIND to fly — a windy day is better for albatross viewing than a calm one. Yellow-eyed penguins come ashore at dusk. Blue penguins emerge after dark. Plan a full afternoon-to-evening visit.",
      "conditions_dependent": true,
      "condition_context": "moderate to windy conditions for albatross"
    },
    {
      "category": "logistics",
      "tip": "Take the scenic Highcliff Road OUT to the peninsula (dramatic views) and the Portobello Road harbour side BACK (easier driving, stops at Portobello for fish and chips). The loop is about 60 km total.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "hidden_gem",
      "tip": "Sandfly Bay (no actual sandflies — named for the wind patterns in the sand) has a wild beach where yellow-eyed penguins sometimes come ashore and sea lions haul out. Free, no tour needed, but maintain a 10-metre distance from all wildlife.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 87,
  "metadata": {
    "island": "south",
    "species": ["royal_albatross", "yellow_eyed_penguin", "blue_penguin", "nz_fur_seal", "nz_sea_lion"],
    "wind_helps": true,
    "multi_species_day": true
  }
}
```

### 14. Hot Water Beach

```json
{
  "destination": "new-zealand",
  "region": "coromandel",
  "name": "Hot Water Beach",
  "slug": "nz-hot-water-beach",
  "description": "Dig your own personal hot pool in the sand at a beach where geothermal water seeps up from underground. The hot spot is a 50-metre stretch of beach where temperatures can reach 64°C underground — dig down, mix with seawater, and create a natural spa. Only works within 2 hours of low tide.",
  "types": ["geothermal", "beach"],
  "location_name": "Hahei",
  "location_point": "SRID=4326;POINT(175.7850 -36.8725)",
  "difficulty": "easy",
  "cost_level": "free",
  "duration_min": 1.0,
  "duration_max": 2.0,
  "seasonal_availability": "year-round",
  "booking_required": false,
  "weather_sensitivity": "high",
  "ideal_conditions": {
    "temperature_min": 15,
    "temperature_max": 30,
    "wind_speed_max": 20,
    "precipitation_probability_max": 10,
    "cloud_cover_max": 40,
    "wave_height_max": 1.0
  },
  "acceptable_conditions": {
    "temperature_min": 5,
    "temperature_max": 35,
    "wind_speed_max": 35,
    "precipitation_probability_max": 50,
    "cloud_cover_max": 80,
    "wave_height_max": 1.5
  },
  "dealbreaker_conditions": {
    "wave_height_above": 2.5
  },
  "logistics": {
    "access": "Hot Water Beach car park, 15 min south of Hahei on the Coromandel Peninsula.",
    "parking": "Paid parking ($10/day). Fills quickly in summer — arrive well before low tide.",
    "facilities": ["toilets", "spade_hire_from_surf_shop"],
    "cell_coverage": "good",
    "nearest_fuel": "Whitianga (30 km)",
    "nearest_medical": "Whitianga Medical Centre (30 km)",
    "estimated_cost_nzd": { "adult": 0, "child": 0, "notes": "Free. Spade hire $5 from the surf shop." },
    "booking_url": null,
    "best_time_of_day": "varies"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "This ONLY works within approximately 2 hours either side of low tide. Check tide times before visiting. At high tide, the hot water area is completely underwater and inaccessible.",
      "conditions_dependent": true,
      "condition_context": "low tide ±2 hours"
    },
    {
      "category": "safety",
      "tip": "The geothermal water can be scalding (64°C+). Test with your hand before sitting down. Always mix with cooler seawater. Children should be closely supervised. Some areas are dangerously hot if you dig too deep.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "timing",
      "tip": "If the tide is right at dawn or dusk, come then — you'll have the hot pools largely to yourself. In summer midday, there can be hundreds of people crowded into the same 50-metre stretch of beach.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 82,
  "metadata": {
    "island": "north",
    "tide_dependent": true,
    "tide_window_hours": 2,
    "combinable_with": "cathedral-cove"
  }
}
```

### 15. Roys Peak Track

```json
{
  "destination": "new-zealand",
  "region": "otago",
  "name": "Roys Peak Track",
  "slug": "nz-roys-peak",
  "description": "One of NZ's most Instagrammed hikes — a relentless 1,200 m climb above Lake Wanaka to a summit with 360° views of the Southern Alps, glaciers, and the lake far below. The iconic ridgeline photo (tiny human on a ridge with vast scenery behind) is one of the most recognizable NZ images. Hard but non-technical.",
  "types": ["hiking", "scenic", "alpine"],
  "location_name": "Wanaka",
  "location_point": "SRID=4326;POINT(169.0575 -44.6256)",
  "difficulty": "hard",
  "cost_level": "free",
  "duration_min": 5.0,
  "duration_max": 7.0,
  "seasonal_availability": "oct-apr (closed 1 oct - 10 nov for lambing)",
  "booking_required": false,
  "weather_sensitivity": "high",
  "ideal_conditions": {
    "temperature_min": 10,
    "temperature_max": 22,
    "wind_speed_max": 20,
    "precipitation_probability_max": 10,
    "cloud_cover_max": 20,
    "visibility_min": 40
  },
  "acceptable_conditions": {
    "temperature_min": 5,
    "temperature_max": 28,
    "wind_speed_max": 35,
    "precipitation_probability_max": 30,
    "cloud_cover_max": 50,
    "visibility_min": 10
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 50,
    "visibility_below": 2,
    "temperature_below": -3,
    "trail_closed": true
  },
  "logistics": {
    "access": "Roys Peak Track car park, Mt Aspiring Road, 6 km west of Wanaka town centre.",
    "parking": "Roadside parking. Fills early in peak summer — arrive by 6 AM on busy days.",
    "facilities": ["none"],
    "cell_coverage": "good at summit, patchy lower down",
    "nearest_fuel": "Wanaka (6 km)",
    "nearest_medical": "Wanaka Medical Centre (6 km)",
    "estimated_cost_nzd": { "adult": 0, "child": 0, "notes": "Free. No facilities on track — bring water, food, sun protection." },
    "booking_url": null,
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "Start at sunrise (or just before) for the best light, fewest people, and to avoid afternoon heat on this exposed, shadeless track. The first hour is in shadow, then the sun hits the upper slopes.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "viewpoint",
      "tip": "The famous Instagram photo spot is NOT at the actual summit — it's on the ridgeline about 20 minutes BEFORE the summit. Look for the narrow ridge with the steep drop-off. Most people queue here for photos on busy days.",
      "conditions_dependent": true,
      "condition_context": "clear skies"
    },
    {
      "category": "hidden_gem",
      "tip": "If Roys Peak is too crowded or you want a less strenuous alternative, Rocky Mountain Track on the other side of the lake gives similarly stunning views with half the effort and a fraction of the crowds.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "preparation",
      "tip": "There is NO shade on the entire track. In summer, you're fully exposed to NZ's intense UV for 5-7 hours. Carry 2-3 litres of water, wear a hat, and apply SPF50+ before starting and reapply at the top.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 82,
  "metadata": {
    "island": "south",
    "elevation_gain_m": 1200,
    "distance_km": 16,
    "closed_for_lambing": "1-oct to 10-nov",
    "instagram_famous": true
  }
}
```

### 16. Māori Cultural Experience (Te Puia, Rotorua)

```json
{
  "destination": "new-zealand",
  "region": "rotorua",
  "name": "Te Puia — Māori Cultural Experience & Geothermal",
  "slug": "nz-te-puia-rotorua",
  "description": "NZ's premier combined cultural and geothermal attraction. Te Puia sits on the Whakarewarewa geothermal valley, home to the Pōhutu Geyser (NZ's most active, erupting 1-2 times per hour). The centre includes a Māori Arts and Crafts Institute (carving and weaving schools), a kiwi house, and cultural performances. Evening packages add a hangi feast and haka performance.",
  "types": ["cultural", "geothermal", "wildlife"],
  "location_name": "Rotorua",
  "location_point": "SRID=4326;POINT(176.2506 -38.1647)",
  "difficulty": "easy",
  "cost_level": "moderate",
  "duration_min": 2.0,
  "duration_max": 4.0,
  "seasonal_availability": "year-round",
  "booking_required": true,
  "weather_sensitivity": "low",
  "ideal_conditions": {
    "temperature_min": 5,
    "temperature_max": 25,
    "wind_speed_max": 30,
    "precipitation_probability_max": 40,
    "cloud_cover_max": 70
  },
  "acceptable_conditions": {
    "temperature_min": -5,
    "temperature_max": 35,
    "wind_speed_max": 60,
    "precipitation_probability_max": 90,
    "cloud_cover_max": 100
  },
  "dealbreaker_conditions": {
    "volcanic_alert_above": 3
  },
  "logistics": {
    "access": "Hemo Road, Rotorua. Well signposted from the city centre. 5 min drive from CBD.",
    "parking": "Large free car park.",
    "facilities": ["toilets", "cafe", "restaurant", "gift_shop", "kiwi_house"],
    "cell_coverage": "good",
    "nearest_fuel": "Rotorua (5 min)",
    "nearest_medical": "Rotorua Hospital (10 min)",
    "estimated_cost_nzd": { "adult": 70, "child": 36, "notes": "Daytime admission. Te Rā evening experience (cultural performance + hangi dinner): $140 adult." },
    "booking_url": "https://www.tepuia.com",
    "best_time_of_day": "morning"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "Pōhutu Geyser erupts 1-2 times per hour — if you arrive and it's not erupting, explore the mud pools and carving school first. Listen for the crowd noise or watch for the steam column from anywhere in the park.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "hidden_gem",
      "tip": "The kiwi house is dimly lit to simulate night (kiwi are nocturnal). Give your eyes 2-3 minutes to adjust and you'll see the kiwi clearly. Many visitors leave too quickly because they can't see anything initially.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "photography",
      "tip": "Geothermal steam is most dramatic on cool mornings and overcast days. On a warm sunny afternoon, the steam disperses quickly and is harder to photograph. Winter visits produce the most spectacular steam columns.",
      "conditions_dependent": true,
      "condition_context": "cool/overcast conditions"
    }
  ],
  "uniqueness_score": 83,
  "metadata": {
    "island": "north",
    "all_weather": true,
    "rainy_day_alternative": true,
    "evening_experience_available": true,
    "kiwi_viewing": true
  }
}
```

### 17. Pancake Rocks & Blowholes (Punakaiki)

```json
{
  "destination": "new-zealand",
  "region": "west-coast",
  "name": "Pancake Rocks & Blowholes",
  "slug": "nz-pancake-rocks-punakaiki",
  "description": "Stacked limestone formations that look like piles of pancakes, sculpted by 30 million years of coastal erosion. At high tide with a good swell, seawater forces through narrow cavities and erupts as dramatic blowholes, shooting spray metres into the air. A short, accessible boardwalk loop along the cliff top.",
  "types": ["scenic", "geological", "coastal"],
  "location_name": "Punakaiki",
  "location_point": "SRID=4326;POINT(171.3261 -42.1147)",
  "difficulty": "easy",
  "cost_level": "free",
  "duration_min": 0.5,
  "duration_max": 1.0,
  "seasonal_availability": "year-round",
  "booking_required": false,
  "weather_sensitivity": "low",
  "ideal_conditions": {
    "temperature_min": 8,
    "temperature_max": 25,
    "wind_speed_max": 40,
    "precipitation_probability_max": 30,
    "cloud_cover_max": 50,
    "wave_height_max": null
  },
  "acceptable_conditions": {
    "temperature_min": 0,
    "temperature_max": 30,
    "wind_speed_max": 60,
    "precipitation_probability_max": 80,
    "cloud_cover_max": 100,
    "wave_height_max": null
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 90
  },
  "logistics": {
    "access": "SH6, Punakaiki. 45 min north of Greymouth, 3 hrs from Christchurch via Arthur's Pass.",
    "parking": "Free car park at the visitor centre.",
    "facilities": ["toilets", "cafe", "visitor_centre"],
    "cell_coverage": "patchy",
    "nearest_fuel": "Greymouth (45 km south) or Westport (55 km north)",
    "nearest_medical": "Greymouth Hospital (45 km)",
    "estimated_cost_nzd": { "adult": 0, "child": 0, "notes": "Free. Open 24 hours. Sunrise and sunset visits are magical." },
    "booking_url": null,
    "best_time_of_day": "any"
  },
  "pro_tips": [
    {
      "category": "timing",
      "tip": "Blowholes are most dramatic at HIGH TIDE with a strong westerly swell. Check tide times and try to visit within an hour of high tide. At low tide, the formations are impressive but the blowholes are silent.",
      "conditions_dependent": true,
      "condition_context": "high tide + westerly swell"
    },
    {
      "category": "photography",
      "tip": "Sunset light on the rocks is spectacular if conditions align. The rocks face roughly west, catching golden hour light. But the West Coast clouds can also create dramatic moody shots in overcast conditions.",
      "conditions_dependent": true,
      "condition_context": "clear sunset"
    },
    {
      "category": "logistics",
      "tip": "This is a quick stop (30-60 min) and works perfectly as a break on the drive between Greymouth and the glaciers. Don't plan a full day around it — combine with the Truman Track (15 min walk to a hidden beach, just 3 km north).",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 75,
  "metadata": {
    "island": "south",
    "tide_enhanced": true,
    "short_stop": true,
    "combinable_with": "truman-track"
  }
}
```

### 18. Doubtful Sound Overnight Cruise

```json
{
  "destination": "new-zealand",
  "region": "southland-fiordland",
  "name": "Doubtful Sound Overnight Cruise",
  "slug": "nz-doubtful-sound-overnight",
  "description": "A remote, pristine fiord ten times the size of Milford Sound but with a fraction of the visitors. Accessible only by boat across Lake Manapōuri and then a bus over Wilmot Pass. The overnight cruise experience includes wildlife spotting (bottlenose dolphins, fur seals, Fiordland crested penguins), kayaking, and — on a calm night — the extraordinary 'sound of silence' when the engines are cut and the fiord's natural sounds envelop you.",
  "types": ["scenic", "cruise", "wildlife", "overnight"],
  "location_name": "Manapōuri / Te Anau",
  "location_point": "SRID=4326;POINT(167.0500 -45.3250)",
  "difficulty": "easy",
  "cost_level": "premium",
  "duration_min": 22.0,
  "duration_max": 26.0,
  "seasonal_availability": "year-round (reduced departures in winter)",
  "booking_required": true,
  "weather_sensitivity": "moderate",
  "ideal_conditions": {
    "temperature_min": 8,
    "temperature_max": 22,
    "wind_speed_max": 20,
    "precipitation_probability_max": 20,
    "cloud_cover_max": 40,
    "visibility_min": 10
  },
  "acceptable_conditions": {
    "temperature_min": 0,
    "temperature_max": 28,
    "wind_speed_max": 50,
    "precipitation_probability_max": 90,
    "cloud_cover_max": 100,
    "visibility_min": 2
  },
  "dealbreaker_conditions": {
    "wind_speed_above": 70
  },
  "logistics": {
    "access": "Departs from Pearl Harbour, Manapōuri (20 min south of Te Anau). Cross Lake Manapōuri by boat, then bus over Wilmot Pass to the fiord.",
    "parking": "Free parking at Pearl Harbour, Manapōuri.",
    "facilities": ["all_meals_included", "cabins", "shared_bathrooms", "kayaks", "tender_boats"],
    "cell_coverage": "none in the fiord",
    "nearest_fuel": "Te Anau (20 km from Manapōuri)",
    "nearest_medical": "Te Anau Medical Centre (20 km)",
    "estimated_cost_nzd": { "adult": 470, "child": 235, "notes": "Overnight cruise including all meals, accommodation, kayaking, and guided nature excursions. Day cruises also available ($270)." },
    "booking_url": "https://www.realjourneys.co.nz/doubtful-sound",
    "best_time_of_day": "departs morning, returns next afternoon"
  },
  "pro_tips": [
    {
      "category": "hidden_gem",
      "tip": "Doubtful Sound is the more rewarding experience compared to Milford for those who have the time and budget. It's far more remote, less crowded (your boat may be the only one in the fiord), and the overnight format allows you to experience the fiord at dawn, which is magical.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "timing",
      "tip": "The 'sound of silence' moment — when the captain cuts the engines in a sheltered arm and everyone goes quiet — is extraordinary on a calm night. You hear only waterfalls, birdsong, and dripping forest. This is less impactful on very windy nights.",
      "conditions_dependent": true,
      "condition_context": "calm evening conditions"
    },
    {
      "category": "wildlife",
      "tip": "Bottlenose dolphins are resident and frequently bow-ride the boat. Fiordland crested penguins are sometimes spotted on rocky shorelines (best Jul-Nov). NZ fur seals are common on rocky outcrops year-round.",
      "conditions_dependent": false,
      "condition_context": null
    },
    {
      "category": "preparation",
      "tip": "There is no cell phone coverage for the entire 24 hours. Embrace the disconnection. Bring a book, binoculars, and a warm layer for evening deck viewing. Seasickness is rarely an issue as the fiord is sheltered.",
      "conditions_dependent": false,
      "condition_context": null
    }
  ],
  "uniqueness_score": 91,
  "metadata": {
    "island": "south",
    "national_park": "fiordland",
    "world_heritage": true,
    "overnight": true,
    "no_cell_coverage": true,
    "species": ["bottlenose_dolphin", "fiordland_crested_penguin", "nz_fur_seal"]
  }
}
```

---

## Condition Scoring Profiles

Below are representative condition scoring profiles used by the decision engine to rate activity conditions. These map to the `ConditionProfile` schema from [CONDITION-MONITORING.md](../02-product/CONDITION-MONITORING.md).

### Profile: Alpine Hiking (Tongariro, Roys Peak, Ben Lomond)

```json
{
  "activity_type": "alpine_hiking",
  "critical_conditions": [
    { "parameter": "wind_speed", "ideal_range": [0, 25], "acceptable_range": [0, 40], "deal_breaker": 55, "weight": 0.30 },
    { "parameter": "visibility", "ideal_range": [20, 100], "acceptable_range": [5, 100], "deal_breaker": 1, "weight": 0.25 },
    { "parameter": "precipitation_probability", "ideal_range": [0, 10], "acceptable_range": [0, 40], "deal_breaker": null, "weight": 0.20 },
    { "parameter": "cloud_cover", "ideal_range": [0, 20], "acceptable_range": [0, 60], "deal_breaker": null, "weight": 0.15 },
    { "parameter": "temperature", "ideal_range": [8, 22], "acceptable_range": [0, 30], "deal_breaker_below": -5, "weight": 0.10 }
  ],
  "special_rules": [
    "If DOC issues track closure → UNSAFE regardless of conditions",
    "If wind chill below -5°C → escalate to POOR minimum",
    "If volcanic alert level > 2 → UNSAFE (Tongariro specific)"
  ]
}
```

### Profile: Glacier Heli-Hike

```json
{
  "activity_type": "glacier_heli_hike",
  "critical_conditions": [
    { "parameter": "cloud_cover", "ideal_range": [0, 30], "acceptable_range": [0, 50], "deal_breaker": 80, "weight": 0.35 },
    { "parameter": "wind_speed", "ideal_range": [0, 15], "acceptable_range": [0, 25], "deal_breaker": 35, "weight": 0.30 },
    { "parameter": "precipitation_probability", "ideal_range": [0, 10], "acceptable_range": [0, 20], "deal_breaker": 60, "weight": 0.20 },
    { "parameter": "visibility", "ideal_range": [15, 100], "acceptable_range": [5, 100], "deal_breaker": 3, "weight": 0.15 }
  ],
  "special_rules": [
    "Helicopter operations have strict aviation weather minimums — operator makes final go/no-go",
    "Cloud ceiling must be above glacier elevation (operator-specific threshold)"
  ]
}
```

### Profile: Marine Wildlife Cruise (Whale Watching, Dolphin Swimming)

```json
{
  "activity_type": "marine_wildlife_cruise",
  "critical_conditions": [
    { "parameter": "wave_height", "ideal_range": [0, 1.0], "acceptable_range": [0, 2.0], "deal_breaker": 3.0, "weight": 0.35 },
    { "parameter": "wind_speed", "ideal_range": [0, 15], "acceptable_range": [0, 30], "deal_breaker": 40, "weight": 0.30 },
    { "parameter": "visibility", "ideal_range": [10, 100], "acceptable_range": [3, 100], "deal_breaker": null, "weight": 0.15 },
    { "parameter": "precipitation_probability", "ideal_range": [0, 20], "acceptable_range": [0, 50], "deal_breaker": null, "weight": 0.10 },
    { "parameter": "sea_temperature", "ideal_range": [12, 22], "acceptable_range": [8, 25], "deal_breaker": null, "weight": 0.10 }
  ],
  "special_rules": [
    "Operator makes final go/no-go based on sea conditions",
    "Rough seas cause seasickness — warn travelers to prepare"
  ]
}
```

### Profile: Stargazing

```json
{
  "activity_type": "stargazing",
  "critical_conditions": [
    { "parameter": "cloud_cover", "ideal_range": [0, 10], "acceptable_range": [0, 30], "deal_breaker": 60, "weight": 0.50 },
    { "parameter": "wind_speed", "ideal_range": [0, 15], "acceptable_range": [0, 25], "deal_breaker": 40, "weight": 0.15 },
    { "parameter": "precipitation_probability", "ideal_range": [0, 5], "acceptable_range": [0, 15], "deal_breaker": 50, "weight": 0.15 },
    { "parameter": "moon_illumination", "ideal_range": [0, 20], "acceptable_range": [0, 50], "deal_breaker": null, "weight": 0.20 }
  ],
  "special_rules": [
    "Moon illumination > 70% significantly degrades Milky Way visibility",
    "Aurora viewing requires Kp index ≥ 4 at NZ latitude",
    "Temperature can drop dramatically at night — always warn about layering"
  ]
}
```

### Profile: Scenic Cruise (Milford Sound, Doubtful Sound)

```json
{
  "activity_type": "scenic_fiord_cruise",
  "critical_conditions": [
    { "parameter": "wind_speed", "ideal_range": [0, 20], "acceptable_range": [0, 50], "deal_breaker": 80, "weight": 0.25 },
    { "parameter": "precipitation_probability", "ideal_range": [0, 20], "acceptable_range": [0, 100], "deal_breaker": null, "weight": 0.15 },
    { "parameter": "cloud_cover", "ideal_range": [0, 30], "acceptable_range": [0, 100], "deal_breaker": null, "weight": 0.20 },
    { "parameter": "visibility", "ideal_range": [10, 100], "acceptable_range": [1, 100], "deal_breaker": null, "weight": 0.20 },
    { "parameter": "temperature", "ideal_range": [8, 22], "acceptable_range": [-5, 30], "deal_breaker": null, "weight": 0.10 }
  ],
  "special_rules": [
    "Rain creates temporary waterfalls — EXCELLENT conditions score when raining",
    "Calm, clear conditions give mirror reflections — different kind of EXCELLENT",
    "Milford Road (SH94) closures prevent access regardless of fiord conditions",
    "No precipitation deal-breaker — both wet and dry conditions are excellent"
  ]
}
```

### Profile: All-Weather / Underground (Caves, Geothermal, Museums)

```json
{
  "activity_type": "all_weather",
  "critical_conditions": [
    { "parameter": "road_conditions", "ideal_range": null, "acceptable_range": null, "deal_breaker": "closed", "weight": 0.80 },
    { "parameter": "temperature", "ideal_range": [0, 30], "acceptable_range": [-10, 40], "deal_breaker": null, "weight": 0.10 },
    { "parameter": "wind_speed", "ideal_range": [0, 40], "acceptable_range": [0, 80], "deal_breaker": null, "weight": 0.10 }
  ],
  "special_rules": [
    "These activities are the swap targets — when outdoor activities are weathered out, these become EXCELLENT",
    "Score is elevated when other nearby activities are rated POOR/UNSAFE"
  ]
}
```

---

## Database Population Strategy

### Phase 1 — MVP Launch (50-60 attractions)

Populate the database with the top 50-60 NZ attractions covering:
- All entries from the South Island and North Island attraction tables in this document series
- Each with full condition profiles, 3-5 pro tips, and complete logistics
- Focus on the most commonly visited and most weather-sensitive attractions first

### Phase 2 — Deep Coverage (100+ attractions)

Expand to include:
- Hidden gems and off-the-beaten-path experiences
- Regional food/wine/cultural experiences
- Accommodation-specific tips (best holiday parks, camping spots)
- Transport segments as "attraction-like" entities (scenic drives, ferry crossings)

### Phase 3 — Community Enrichment

Add user-contributed:
- New pro tips validated against trip feedback
- Updated logistics (price changes, facility changes)
- Seasonal condition refinements based on actual trip data
- Photo-validated viewpoint tips
