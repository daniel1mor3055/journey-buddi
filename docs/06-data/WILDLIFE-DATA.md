# Wildlife Data

## Overview

Wildlife viewing is a core attraction for travelers in New Zealand — dolphins, whales, penguins, seals, albatross, kiwi, and glowworms are bucket-list experiences. Unlike weather or tides, wildlife data is not primarily API-driven. Instead, it is a curated knowledge base of species behavior patterns, seasonal windows, condition dependencies, and location-specific intelligence. This document specifies the data structure, content, and integration approach for Journey Buddi's wildlife knowledge system.

## Architecture: Knowledge Base, Not API

Wildlife data in Journey Buddi is structured as a knowledge base with two tiers:

1. **Structured data** — Species profiles, seasonal calendars, condition rules, and location bindings stored in the database and queryable by the AI agent.
2. **Unstructured knowledge** — Detailed natural history, viewing tips, and behavioral notes stored as text chunks in the vector store for RAG retrieval.

```
┌──────────────────────────────────────────────────────────────────┐
│                    WILDLIFE KNOWLEDGE BASE                       │
│                                                                  │
│  ┌─────────────────────┐     ┌──────────────────────────────┐   │
│  │  Structured Data     │     │  Unstructured Knowledge       │   │
│  │  (PostgreSQL)        │     │  (Vector Store / RAG)         │   │
│  │                      │     │                               │   │
│  │  - Species profiles  │     │  - Natural history detail     │   │
│  │  - Seasonal windows  │     │  - Viewing tips & stories     │   │
│  │  - Condition rules   │     │  - Research paper excerpts    │   │
│  │  - Location bindings │     │  - DOC conservation info      │   │
│  │  - Activity links    │     │  - Local guide knowledge      │   │
│  └──────────┬───────────┘     └──────────────┬───────────────┘   │
│             │                                │                    │
│             ▼                                ▼                    │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │              AI AGENT (Buddi)                              │   │
│  │                                                            │   │
│  │  Queries structured data for scheduling decisions.         │   │
│  │  Retrieves RAG chunks for rich conversational responses.   │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## NZ Wildlife Species Profiles

### Marine Mammals

#### Dolphins

| Species | Best Locations | Peak Season | Best Time of Day | Condition Dependencies |
|---------|---------------|-------------|-----------------|----------------------|
| Dusky Dolphin | Kaikōura | Year-round (peak Nov–Apr) | Morning | Calm seas (<1.5m swell), good visibility |
| Hector's Dolphin | Akaroa, Banks Peninsula | Nov–Apr | Any (daytime) | Calm conditions, low swell |
| Bottlenose Dolphin | Bay of Islands, Marlborough Sounds | Year-round | Morning–midday | Moderate conditions tolerable |
| Common Dolphin | Bay of Islands, Hauraki Gulf | Year-round | Morning | Calm to moderate seas |

```python
DUSKY_DOLPHIN = WildlifeSpecies(
    id="dusky-dolphin",
    common_name="Dusky Dolphin",
    scientific_name="Lagenorhynchus obscurus",
    category="marine_mammal",
    locations=[
        WildlifeLocation(
            name="Kaikōura",
            lat=-42.40, lon=173.68,
            reliability="high",
            notes="Year-round pods of 100-1000. Kaikōura Canyon brings deep water close to shore.",
        ),
    ],
    seasonal_calendar={
        "jan": {"activity": "high", "notes": "Peak season, large pods, swimming encounters available"},
        "feb": {"activity": "high", "notes": "Peak season"},
        "mar": {"activity": "high", "notes": "Late summer, still excellent"},
        "apr": {"activity": "moderate", "notes": "Transitioning, pods moving"},
        "may": {"activity": "moderate", "notes": "Smaller pods"},
        "jun": {"activity": "low", "notes": "Winter, fewer boats operating"},
        "jul": {"activity": "low", "notes": "Winter"},
        "aug": {"activity": "low", "notes": "Winter"},
        "sep": {"activity": "moderate", "notes": "Spring, activity increasing"},
        "oct": {"activity": "moderate", "notes": "Spring"},
        "nov": {"activity": "high", "notes": "Season opening up"},
        "dec": {"activity": "high", "notes": "Peak begins"},
    },
    condition_rules=[
        ConditionRule(parameter="wave_height", max_value=1.5, unit="m", impact="Boats may not operate in >1.5m swell"),
        ConditionRule(parameter="wind_speed", max_value=30, unit="kmh", impact="Poor visibility, choppy conditions"),
        ConditionRule(parameter="visibility", min_value=5, unit="km", impact="Hard to spot dolphins in poor visibility"),
    ],
    viewing_type="boat_tour",
    booking_required=True,
    typical_duration_hours=2.5,
    cost_nzd=180,
    conservation_status="Least Concern",
)
```

#### Whales

| Species | Best Locations | Peak Season | Viewing Method | Condition Dependencies |
|---------|---------------|-------------|----------------|----------------------|
| Sperm Whale | Kaikōura | Year-round (males), peak Dec–Mar | Boat tour | Calm seas, good acoustics for hydrophone |
| Humpback Whale | Kaikōura (migration) | Jun–Jul (northward), Sep–Nov (southward) | Boat tour | Calm seas |
| Orca | Nationwide coastal | Year-round (unpredictable) | Shore/boat | Tide (follow stingrays in shallows) |
| Southern Right Whale | Auckland Islands (rare mainland) | Jun–Oct | Shore | Very rare mainland, mostly subantarctic |

#### Seals

| Species | Best Locations | Peak Season | Best Time | Condition Dependencies |
|---------|---------------|-------------|-----------|----------------------|
| NZ Fur Seal | Kaikōura, Abel Tasman, Milford Sound, Otago Peninsula, Cape Palliser | Year-round (pups Nov–Feb) | Any | Low tide best for rock platforms. Maintain 10m distance. |

### Penguins

| Species | Best Locations | Peak Season | Best Time of Day | Condition Dependencies |
|---------|---------------|-------------|-----------------|----------------------|
| Yellow-Eyed Penguin (Hoiho) | Otago Peninsula, Curio Bay, Catlins | Year-round (best Oct–Mar) | Late afternoon (4–6pm) — returning from sea | Minimal disturbance, stay in hides |
| Blue Penguin (Kororā) | Oamaru, Banks Peninsula, Wellington | Year-round (best Oct–Mar) | Dusk — emerging from sea | Darkness required, red-light viewing only |

```python
YELLOW_EYED_PENGUIN = WildlifeSpecies(
    id="yellow-eyed-penguin",
    common_name="Yellow-Eyed Penguin (Hoiho)",
    scientific_name="Megadyptes antipodes",
    category="seabird",
    conservation_status="Endangered",
    locations=[
        WildlifeLocation(
            name="Otago Peninsula",
            lat=-45.83, lon=170.72,
            reliability="high",
            notes="Best viewed from DOC hides at Sandfly Bay or Penguin Place (private reserve).",
        ),
        WildlifeLocation(
            name="Curio Bay, Catlins",
            lat=-46.66, lon=169.10,
            reliability="moderate",
            notes="Wild colony on the beach. Stay behind barriers.",
        ),
    ],
    best_time_of_day="late_afternoon",
    best_time_detail="4:00 PM – 6:00 PM, when penguins return from the sea and waddle up the beach to their nests.",
    condition_rules=[
        ConditionRule(parameter="precipitation_probability", max_value=50, unit="%", impact="Penguins still come ashore in rain, but viewing is unpleasant"),
        ConditionRule(parameter="wind_speed", max_value=40, unit="kmh", impact="Strong wind doesn't deter penguins but makes viewing uncomfortable"),
    ],
    viewing_tips=[
        "Stay at least 10m from penguins — they are easily stressed.",
        "Use hides/blinds where available (Sandfly Bay has DOC hides).",
        "No flash photography. Hoiho are highly sensitive to disturbance.",
        "Arrive 30 minutes before expected return time and wait quietly.",
        "If a penguin seems distressed (calling, not moving toward nest), back away.",
    ],
    viewing_type="self_guided",
    booking_required=False,
    typical_duration_hours=1.5,
    cost_nzd=0,
)
```

### Birds

| Species | Best Locations | Season | Time of Day | Conditions |
|---------|---------------|--------|-------------|------------|
| Royal Albatross | Taiaroa Head, Dunedin | Year-round (nesting Nov–Sep) | Daytime | Wind! Albatross need wind to soar — windier = better |
| Kiwi | Stewart Island, Zealandia (Wellington), Tongariro | Year-round | Night (after dark) | Dark moon phase, quiet conditions, guided tours |
| Tūī, Bellbird, Kea, Kākā | Various forest/alpine locations | Year-round | Morning | Calm, clear mornings best for birdsong |
| Gannet | Cape Kidnappers (Hawke's Bay) | Nov–Feb (colony active) | Daytime | Low tide for beach access (or overland track) |

### Glowworms

| Species | Best Locations | Season | Time | Conditions |
|---------|---------------|--------|------|------------|
| Arachnocampa luminosa | Waitomo Caves, Te Anau Caves, Waimarino Glow Worm Dell (Hokitika), natural caves/overhangs | Year-round | Night | Complete darkness needed. Damp conditions = brighter glow. |

```python
GLOWWORM = WildlifeSpecies(
    id="glowworm",
    common_name="New Zealand Glowworm",
    scientific_name="Arachnocampa luminosa",
    category="invertebrate",
    locations=[
        WildlifeLocation(
            name="Waitomo Caves",
            lat=-38.26, lon=175.10,
            reliability="guaranteed",
            notes="Commercial cave tours. Boat ride through glowworm grotto.",
        ),
        WildlifeLocation(
            name="Waimarino Glow Worm Dell, Hokitika",
            lat=-42.45, lon=171.21,
            reliability="high",
            notes="Free, self-guided. Short walk from town. Best on dark, damp nights.",
        ),
        WildlifeLocation(
            name="Te Anau Caves",
            lat=-45.42, lon=167.72,
            reliability="guaranteed",
            notes="Boat trip across Lake Te Anau + cave tour.",
        ),
    ],
    condition_rules=[
        ConditionRule(parameter="moon_illumination", max_value=30, unit="%", impact="Brighter moon reduces glowworm visibility (for outdoor locations)"),
        ConditionRule(parameter="precipitation_type", preferred_value="rain", impact="Damp conditions make glowworms brighter"),
    ],
    viewing_tips=[
        "Turn off all lights — even phone screens. Let eyes adjust for 5 minutes.",
        "Rainy or drizzly nights produce the brightest displays (outdoor locations).",
        "Cave locations are weather-independent — good rainy-day option.",
        "Don't touch the glowworm threads (sticky silk lines hanging down).",
        "Whisper — loud noise can cause glowworms to dim.",
    ],
    best_time_of_day="night",
    viewing_type="self_guided",
    typical_duration_hours=1,
    cost_nzd=0,
)
```

## How Conditions Affect Wildlife Viewing

### Condition-Wildlife Matrix

| Condition | Dolphins | Whales | Penguins | Kiwi | Albatross | Seals | Glowworms |
|-----------|----------|--------|----------|------|-----------|-------|-----------|
| Calm seas | Essential | Essential | N/A | N/A | Less active | N/A | N/A |
| Strong wind | Bad | Bad | OK | OK | Excellent | OK | N/A |
| Rain | Bad (visibility) | Bad | OK (they don't mind) | OK (active in rain) | OK | OK | Excellent (outdoor) |
| Low tide | N/A | N/A | N/A | N/A | N/A | Best (rock platforms) | N/A |
| Full moon | N/A | N/A | OK | Bad (too bright) | N/A | N/A | Bad (outdoor) |
| New moon | N/A | N/A | OK | Excellent | N/A | N/A | Excellent |
| Dusk/Dawn | Good | Good | Dusk essential | After dark | Good | Any | After dark |

### Wildlife Condition Scoring

The AI agent uses this matrix to score wildlife activities against current conditions:

```python
class WildlifeConditionScorer:
    def score_wildlife_activity(
        self,
        species: WildlifeSpecies,
        weather: WeatherCondition,
        tide: TideCondition | None,
        solar: SolarCondition,
    ) -> WildlifeScore:
        scores = []

        for rule in species.condition_rules:
            value = self._get_condition_value(rule.parameter, weather, tide, solar)
            if value is None:
                continue

            if rule.max_value is not None and value > rule.max_value:
                scores.append(0)
            elif rule.min_value is not None and value < rule.min_value:
                scores.append(0)
            elif rule.preferred_value is not None:
                scores.append(100 if str(value) == rule.preferred_value else 50)
            else:
                scores.append(100)

        seasonal_score = self._get_seasonal_score(species, datetime.now())

        overall = (
            (sum(scores) / len(scores) if scores else 80) * 0.6 +
            seasonal_score * 0.4
        )

        return WildlifeScore(
            species_id=species.id,
            score=round(overall),
            rating=self._score_to_rating(overall),
            factors=self._explain_factors(species, weather, tide, solar),
        )

    def _get_seasonal_score(self, species: WildlifeSpecies, dt: datetime) -> float:
        month_key = dt.strftime("%b").lower()
        activity = species.seasonal_calendar.get(month_key, {}).get("activity", "moderate")
        return {"high": 100, "moderate": 60, "low": 30, "none": 0}.get(activity, 50)
```

## Data Structure

### Database Schema

```sql
CREATE TABLE wildlife_species (
    id VARCHAR(100) PRIMARY KEY,
    common_name VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255),
    category VARCHAR(50) NOT NULL,  -- marine_mammal, seabird, bird, invertebrate, reptile
    conservation_status VARCHAR(50),
    best_time_of_day VARCHAR(50),   -- morning, afternoon, dusk, night, any
    best_time_detail TEXT,
    viewing_type VARCHAR(50),       -- boat_tour, self_guided, guided_walk
    booking_required BOOLEAN DEFAULT FALSE,
    typical_duration_hours FLOAT,
    cost_nzd FLOAT DEFAULT 0,
    seasonal_calendar JSONB NOT NULL,
    condition_rules JSONB NOT NULL,
    viewing_tips TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE wildlife_locations (
    id SERIAL PRIMARY KEY,
    species_id VARCHAR(100) REFERENCES wildlife_species(id),
    name VARCHAR(255) NOT NULL,
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL,
    reliability VARCHAR(50),        -- guaranteed, high, moderate, low, unpredictable
    notes TEXT,
    access_notes TEXT,
    best_months VARCHAR(50)[],
    UNIQUE(species_id, name)
);

CREATE TABLE wildlife_sightings (
    id SERIAL PRIMARY KEY,
    species_id VARCHAR(100) REFERENCES wildlife_species(id),
    location_id INT REFERENCES wildlife_locations(id),
    sighted_at TIMESTAMP NOT NULL,
    reported_by VARCHAR(50),        -- user, inaturalist, doc, guide
    count INT,
    notes TEXT,
    conditions_snapshot JSONB
);
```

### Wildlife Knowledge Entry (RAG Content)

Each species has detailed knowledge chunks stored in the vector store for RAG retrieval:

```python
wildlife_knowledge_chunks = [
    {
        "species_id": "dusky-dolphin",
        "chunk_type": "natural_history",
        "content": (
            "Dusky dolphins at Kaikōura are among the most acrobatic dolphins in the world. "
            "The pods here can number from 100 to over 1,000 individuals. They feed at night "
            "on the deep scattering layer organisms brought close to shore by the Kaikōura Canyon — "
            "a 1,600m deep submarine trench just 800m offshore. During the day, they rest, socialize, "
            "and perform spectacular aerial displays. The best encounters happen in the morning "
            "when pods are active and playful near the surface."
        ),
        "metadata": {
            "location": "Kaikōura",
            "source": "DOC + marine biology research",
            "confidence": "high",
        },
    },
    {
        "species_id": "yellow-eyed-penguin",
        "chunk_type": "viewing_guide",
        "content": (
            "The yellow-eyed penguin (hoiho) is one of the world's rarest penguin species, with "
            "fewer than 4,000 remaining. At Sandfly Bay on the Otago Peninsula, penguins return "
            "from the sea between 4–6 PM. The DOC has built wooden hides on the hillside above "
            "the beach — arrive early, get settled, and wait. The penguins waddle up the beach "
            "and through the sand dunes to their nests in the vegetation. They are extremely shy; "
            "if they detect humans on the beach, they will wait at the water's edge until it's "
            "safe, sometimes standing in the surf for hours. Always use the hides, never approach "
            "on the beach, and keep completely silent."
        ),
        "metadata": {
            "location": "Otago Peninsula",
            "source": "DOC, Penguin Place guides",
            "confidence": "high",
        },
    },
    {
        "species_id": "kiwi",
        "chunk_type": "viewing_guide",
        "content": (
            "Stewart Island (Rakiura) is the only place in New Zealand where you can see kiwi "
            "in the wild without a guide — though guided tours (like Ruggedy Range) dramatically "
            "increase your chances. Stewart Island kiwi (Apteryx australis lawryi) are unique "
            "because they are sometimes active during the day, unlike mainland kiwi which are "
            "strictly nocturnal. The best viewing is on Ocean Beach at dusk — kiwi come out to "
            "forage in the kelp and sand. Wear dark clothing, use a red-filtered torch only, "
            "speak in whispers, and move slowly. New moon nights are best because the beach is "
            "darker and kiwi feel safer venturing out."
        ),
        "metadata": {
            "location": "Stewart Island",
            "source": "DOC, Ruggedy Range guides",
            "confidence": "high",
        },
    },
]
```

## Data Sources

### DOC (Department of Conservation) New Zealand

- **Website**: https://www.doc.govt.nz
- **What we extract**: Species profiles, conservation status, location information, viewing guidelines, seasonal guidance, safety rules
- **Integration method**: Manual curation at knowledge base creation time, periodic review (quarterly)
- **License**: Crown copyright, generally free to use with attribution

### iNaturalist API

- **Purpose**: Supplement knowledge base with recent observation data to detect seasonal patterns and unusual sightings
- **Endpoint**: `GET https://api.inaturalist.org/v1/observations?taxon_name={species}&place_id=6803&order=desc&order_by=observed_on`
- **Place ID 6803**: New Zealand
- **Rate limit**: 100 requests/minute (generous)
- **Use case**: Periodically (weekly) query recent observations for key species to update seasonal activity patterns

```python
class INaturalistClient:
    BASE_URL = "https://api.inaturalist.org/v1"

    async def get_recent_observations(
        self, species_name: str, days: int = 30
    ) -> list[dict]:
        params = {
            "taxon_name": species_name,
            "place_id": 6803,  # New Zealand
            "d1": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
            "order": "desc",
            "order_by": "observed_on",
            "per_page": 50,
            "quality_grade": "research",  # verified observations only
        }
        response = await self.client.get(f"{self.BASE_URL}/observations", params=params)
        data = response.json()

        return [
            {
                "observed_on": obs["observed_on"],
                "location": obs["location"],
                "place_guess": obs["place_guess"],
                "photos": [p["url"] for p in obs.get("photos", [])],
                "description": obs.get("description"),
            }
            for obs in data.get("results", [])
        ]
```

### Marine Research Papers

- **Purpose**: Deep behavioral knowledge for the AI's conversational responses
- **Sources**: University of Otago marine biology, NIWA marine research, DOC science reports
- **Integration**: Key findings are distilled into RAG knowledge chunks during curation
- **Examples**:
  - Sperm whale dive patterns and surface intervals at Kaikōura
  - Hector's dolphin population trends at Banks Peninsula
  - Penguin breeding success rates by year and location

### Local Guide Knowledge

- **Purpose**: Expert-level tips that only experienced guides know
- **Collection method**: Interviews, trip reports, guide partnerships
- **Examples**:
  - "At Kaikōura, the 7:30am Dolphin Encounter trip sees the most acrobatic behavior because the pods have just finished night feeding"
  - "At Sandfly Bay, the penguins use the track on the left side of the dunes 80% of the time — position your hide accordingly"

## Integration with AI Agent

### How Buddi Uses Wildlife Data

1. **Trip planning phase**: When building an itinerary, Buddi checks which wildlife species are active at the traveler's destinations during their travel dates, and suggests relevant wildlife activities.

2. **Daily briefing**: Buddi mentions wildlife opportunities for the day:
   > *"This afternoon at Otago Peninsula, yellow-eyed penguins typically return to shore between 4–6pm. I've scheduled your visit for 3:30pm so you can get settled in the viewing hides before they arrive."*

3. **Condition-triggered alerts**: When conditions align exceptionally well:
   > *"Perfect conditions for dolphin swimming tomorrow in Kaikōura — flat calm seas forecast and water visibility is excellent. The 7:30am trip has the most active pods."*

4. **Conversational depth**: When users ask about wildlife, Buddi retrieves RAG chunks to provide expert-level responses:
   > User: *"Tell me about the penguins at Otago Peninsula"*
   > Buddi: *"The yellow-eyed penguin — or hoiho — is one of the world's rarest penguins, with fewer than 4,000 remaining. At Sandfly Bay..."* (pulled from knowledge chunks)

### Query Flow

```python
async def get_wildlife_opportunities(
    self, lat: float, lon: float, date: datetime,
    weather: WeatherCondition, tide: TideCondition | None, solar: SolarCondition,
) -> list[WildlifeOpportunity]:
    nearby_species = await self.db.get_species_near(lat, lon, radius_km=50)

    opportunities = []
    for species in nearby_species:
        score = self.scorer.score_wildlife_activity(species, weather, tide, solar)
        if score.score >= 40:
            knowledge = await self.vector_store.search(
                query=f"{species.common_name} viewing tips {species.locations[0].name}",
                top_k=2,
            )
            opportunities.append(WildlifeOpportunity(
                species=species,
                score=score,
                knowledge_snippets=knowledge,
                best_viewing_window=self._calculate_viewing_window(species, solar),
            ))

    return sorted(opportunities, key=lambda o: o.score.score, reverse=True)
```

## Maintenance and Updates

### Update Frequency

| Data Type | Update Frequency | Method |
|-----------|-----------------|--------|
| Species profiles | Quarterly | Manual review |
| Seasonal calendars | Annually | Update based on DOC reports + iNaturalist trends |
| Location data | As needed | When new sites discovered or access changes |
| RAG knowledge chunks | Quarterly | Add new content, refresh existing |
| iNaturalist observations | Weekly (automated) | Background task queries API |
| Conservation status | As changed | Monitor DOC announcements |

### Adding a New Species

Template for adding a new species to the knowledge base:

1. Create `WildlifeSpecies` record with all structured fields
2. Add `WildlifeLocation` records for each viewing site
3. Write 3–5 RAG knowledge chunks (natural history, viewing guide, seasonal notes, safety)
4. Add condition rules
5. Link to relevant activities in the itinerary system

## Cross-References

- **Knowledge system architecture**: See [Knowledge System](../03-ai/KNOWLEDGE-SYSTEM.md)
- **Condition scoring for activities**: See [Condition Monitoring](../02-product/CONDITION-MONITORING.md)
- **Activity guidance with wildlife**: See [Activity Guidance](../02-product/ACTIVITY-GUIDANCE.md)
- **RAG integration**: See [AI Agent Overview](../03-ai/AI-AGENT-OVERVIEW.md)
- **Destination knowledge base**: See [Destination Knowledge Base](./DESTINATION-KNOWLEDGE-BASE.md)
