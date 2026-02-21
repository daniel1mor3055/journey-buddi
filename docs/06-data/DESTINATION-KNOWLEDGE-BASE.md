# Destination Knowledge Base

## Overview

The destination knowledge base is Journey Buddi's core intelligence about places — the deep, local-expert-level content that transforms generic trip planning into the kind of guidance you'd get from a friend who has lived in and explored a region for years. It stores structured data about attractions, logistics, and conditions alongside unstructured content (stories, tips, insights) that the AI agent retrieves via RAG to deliver conversational, contextually rich responses.

This document specifies the architecture, content model, population process, quality standards, and scaling strategy for the knowledge base.

## Knowledge Base Architecture

### Two-Tier Data Model

The knowledge base operates across two complementary storage layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DESTINATION KNOWLEDGE BASE                           │
│                                                                         │
│  TIER 1: STRUCTURED DATA (PostgreSQL)                                  │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  Destinations  →  Regions  →  Attractions  →  Activities    │       │
│  │                                                              │       │
│  │  Queryable fields:                                          │       │
│  │  - Location (lat/lon, region, nearest town)                 │       │
│  │  - Category (hiking, scenic, wildlife, cultural)            │       │
│  │  - Duration, difficulty, cost                               │       │
│  │  - Condition requirements (weather, tide, time of day)      │       │
│  │  - Availability (seasonal, booking, capacity)               │       │
│  │  - Logistics (parking, access, facilities)                  │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  TIER 2: UNSTRUCTURED KNOWLEDGE (Vector Store / RAG)                   │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  Knowledge chunks indexed by embedding similarity:          │       │
│  │                                                              │       │
│  │  - Pro tips ("The viewpoint 200m past the official one...")  │       │
│  │  - Stories ("This valley was carved by glaciers 10,000...")  │       │
│  │  - Area context ("Fiordland gets 200 days of rain/year...")  │       │
│  │  - Logistics detail ("The road to Milford closes at...")    │       │
│  │  - Seasonal notes ("In March the beech forest turns...")    │       │
│  │  - Safety notes ("The Tongariro Crossing requires...")      │       │
│  │  - Photography guides ("For the best mirror reflection...") │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  AI AGENT INTERFACE                                                     │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  Structured queries: "What attractions near Queenstown      │       │
│  │    are suitable for rainy weather, moderate fitness,         │       │
│  │    and take less than 3 hours?"                              │       │
│  │                                                              │       │
│  │  RAG retrieval: "Tell me about the Routeburn Track" →       │       │
│  │    retrieves pro tips, stories, logistics, conditions       │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why Two Tiers?

| Need | Tier 1 (Structured) | Tier 2 (RAG) |
|------|-------------------|--------------|
| "Find activities near Queenstown suitable for rain" | SQL query on conditions, location | N/A |
| "What's special about Milford Sound?" | Basic description | Rich narrative, tips, stories |
| "Can I do the Tongariro Crossing in winter?" | Seasonal availability flag | Detailed safety notes, gear requirements |
| "Recommend a sunset viewpoint" | Filter by `sunset_worthy: true` | Specific photography angles, parking tips |
| Schedule optimization | Duration, location, conditions | N/A |
| Conversational response | Template data | Natural, expert-quality knowledge |

## Content Categories

### 1. Attractions (Structured)

Core data for each point of interest. See [Knowledge System](../03-ai/KNOWLEDGE-SYSTEM.md) for the full `AttractionKnowledge` schema. Key fields:

```python
class Attraction(BaseModel):
    id: str
    name: str
    destination_id: str
    region: str
    location: GeoPoint
    categories: list[str]        # hiking, scenic, wildlife, cultural, water, adventure
    description: str
    duration_hours: Range         # {min: 1.5, max: 3.0}
    difficulty: str               # easy, moderate, hard, extreme
    cost: Cost                    # {amount: 0, currency: "NZD", notes: "Free"}
    condition_profile: ConditionProfile
    availability: Availability
    logistics: Logistics
    tags: list[str]               # sunset_worthy, photography, family_friendly, rainy_day
    related_attractions: list[str]
```

### 2. Pro Tips (RAG)

Expert-level advice tagged by category:

| Tip Category | Example |
|-------------|---------|
| `timing` | "Arrive at Roy's Peak trailhead before 6am to avoid the crowd and catch sunrise from the top" |
| `viewpoint` | "The official viewpoint at Lake Matheson is good, but walk 200m further to the Reflection Island jetty for a better angle with less people" |
| `preparation` | "Pack sandfly repellent for Milford Sound — the sandflies are legendary and relentless" |
| `hidden_gem` | "The small waterfall 500m up the Routeburn before the first swing bridge is a perfect swimming hole that most people walk past" |
| `photography` | "For the classic Mitre Peak mirror reflection, you need: still water (no wind), early morning light, and the viewing platform at Milford Sound Lodge" |
| `food` | "The meat pie at the Fairlie Bakehouse on the way to Mt Cook is legendary — worth a 10-minute detour" |
| `logistics` | "The Milford Road tunnel has a traffic light with up to 25-minute waits — factor this into your schedule" |
| `safety` | "The Tongariro Alpine Crossing should not be attempted in winter without alpine experience, crampons, and an ice axe" |

### 3. Stories & Context (RAG)

Narrative content that gives places meaning and depth:

```python
class StoryChunk(BaseModel):
    attraction_id: str
    chunk_type: str          # "geological", "cultural", "historical", "ecological", "personal"
    content: str             # 100-500 words of rich narrative
    source: str              # DOC, guidebook, local guide, research
    confidence: str          # high, medium, low

# Example
StoryChunk(
    attraction_id="milford-sound",
    chunk_type="geological",
    content=(
        "Milford Sound — or Piopiotahi in te reo Māori — was carved by glaciers over "
        "hundreds of thousands of years. The fiord extends 15km inland from the Tasman Sea "
        "and reaches depths of 291 meters. Mitre Peak, the iconic 1,692m summit that rises "
        "directly from the water, is one of the most photographed landmarks in New Zealand. "
        "The fiord receives an average of 6,813mm of rainfall per year — one of the wettest "
        "inhabited places on Earth. This extreme rainfall creates dozens of temporary waterfalls "
        "that cascade down the cliff faces after rain, making rainy days arguably the most "
        "spectacular time to visit. A permanent freshwater layer on the surface (from all the "
        "rain) creates unique conditions where deep-water species like black coral grow at "
        "unusually shallow depths."
    ),
    source="DOC interpretive materials, geological surveys",
    confidence="high",
)
```

### 4. Area Knowledge (RAG)

Regional context that applies to multiple attractions:

```python
AreaKnowledge(
    region="fiordland",
    chunk_type="climate",
    content=(
        "Fiordland has a maritime climate with rainfall significantly higher than the rest of "
        "New Zealand. Milford Sound averages 182 rain days per year. The key planning insight: "
        "don't cancel a Fiordland day because of rain. Rainy days create hundreds of temporary "
        "waterfalls, the most dramatic scenery, and Stirling Falls becomes a thundering cascade. "
        "The locals say 'If you visit Milford Sound on a sunny day, you'll see Milford Sound. "
        "If you visit on a rainy day, you'll see Milford Sound at its best.' Pack proper rain "
        "gear and embrace it."
    ),
)
```

### 5. Transport & Logistics (Structured + RAG)

Practical travel information between locations:

```python
class TransportInfo(BaseModel):
    origin: str               # region or attraction ID
    destination: str
    mode: str                 # drive, ferry, flight, walk, bus
    duration_hours: Range
    distance_km: float
    route_notes: str          # "Via SH94, single-lane sections, watch for kea on road"
    fuel_stops: list[str]     # "Last fuel at Te Anau — 120km to Milford with no services"
    road_type: str            # sealed, gravel, motorway, alpine pass
    seasonal_closures: str    # "Milford Road may close in winter snow/avalanche"
    scenic_rating: int        # 1-5, how scenic is this drive?
    campervan_suitable: bool
    key_stops: list[str]      # recommended stops along the way
```

### 6. Logistics & Practical (RAG)

Granular practical details:

| Topic | Example Content |
|-------|----------------|
| Cell coverage | "No cell coverage between Homer Tunnel and Milford Sound (45 min drive). Download offline maps before leaving Te Anau." |
| Water | "Tap water is drinkable throughout NZ. Stream water above huts is generally safe but use treatment below farmland." |
| Freedom camping | "Freedom camping is restricted in many areas. The CamperMate app shows legal sites. Fines are $200+." |
| Booking lead times | "Milford Sound cruises book out 2-3 weeks ahead in peak season (Dec-Feb). Book early." |
| Fuel | "Fuel in remote areas (Haast, Milford) costs 20-30% more than cities. Fill up in Queenstown or Te Anau." |
| Supermarkets | "The last supermarket before the West Coast is in Cromwell. Stock up." |

## How to Add a New Destination

### Templated Process

Adding a new destination follows a structured workflow to ensure completeness and consistency.

#### Step 1: Create Destination Record

```python
new_destination = Destination(
    id="queenstown",
    name="Queenstown",
    country="NZ",
    region="Otago",
    center_lat=-45.0312,
    center_lon=168.6626,
    timezone="Pacific/Auckland",
    description="Adventure capital of New Zealand...",
    climate_summary="Four distinct seasons, continental climate...",
    best_months=["dec", "jan", "feb", "mar", "oct", "nov"],
    minimum_days=3,
    ideal_days=5,
)
```

#### Step 2: Add Attractions (Minimum 15 per destination)

For each attraction, populate:
- [ ] Basic info (name, location, categories, description)
- [ ] Duration and difficulty
- [ ] Cost information
- [ ] Condition profile (weather sensitivity, ideal/acceptable/dealbreaker conditions)
- [ ] Availability (seasonal, booking, capacity)
- [ ] Logistics (parking, access, facilities, cell coverage)
- [ ] Tags (sunset_worthy, family_friendly, rainy_day, etc.)

#### Step 3: Add Pro Tips (Minimum 3 per attraction)

For each attraction, create at least 3 pro tips covering:
- [ ] Best timing or approach
- [ ] Hidden gem or lesser-known aspect
- [ ] Practical preparation advice

#### Step 4: Add Stories (Minimum 1 per attraction)

Write or curate at least one narrative chunk per attraction covering geological, cultural, or ecological significance.

#### Step 5: Add Area Knowledge (Minimum 5 per destination)

Regional chunks covering:
- [ ] Climate and weather patterns
- [ ] Cultural context and te reo Māori significance
- [ ] Transport and logistics
- [ ] Safety considerations
- [ ] Seasonal character

#### Step 6: Add Transport Links

For every pair of commonly visited locations within the destination:
- [ ] Drive time and distance
- [ ] Route notes and scenic stops
- [ ] Fuel and services
- [ ] Road type and conditions

#### Step 7: Add Wildlife Data

For each wildlife species viewable at the destination:
- [ ] Species profile (if not already in the global species database)
- [ ] Location-specific viewing information
- [ ] Seasonal and condition notes

#### Step 8: Review and Quality Check

- [ ] Run completeness check (all required fields populated)
- [ ] Verify GPS coordinates are accurate
- [ ] Cross-reference with DOC and tourism NZ sources
- [ ] Test RAG retrieval for key queries
- [ ] Review by someone who has visited the destination

### Destination Completeness Scoring

```python
def score_destination_completeness(destination_id: str) -> dict:
    attractions = get_attractions(destination_id)
    tips = get_pro_tips(destination_id)
    stories = get_stories(destination_id)
    area_knowledge = get_area_knowledge(destination_id)
    transport = get_transport_links(destination_id)

    scores = {
        "attractions": min(100, len(attractions) / 15 * 100),
        "tips_per_attraction": min(100, (len(tips) / max(len(attractions), 1)) / 3 * 100),
        "stories": min(100, len(stories) / max(len(attractions), 1) * 100),
        "area_knowledge": min(100, len(area_knowledge) / 5 * 100),
        "transport_links": min(100, len(transport) / 10 * 100),
        "condition_profiles": sum(1 for a in attractions if a.condition_profile) / max(len(attractions), 1) * 100,
        "logistics_complete": sum(1 for a in attractions if a.logistics.parking) / max(len(attractions), 1) * 100,
    }

    overall = sum(scores.values()) / len(scores)
    return {
        "destination_id": destination_id,
        "overall_score": round(overall, 1),
        "breakdown": scores,
        "ready_for_production": overall >= 80,
    }
```

## Quality Assurance

### Content Quality Standards

| Standard | Requirement |
|----------|-------------|
| **Accuracy** | All facts verified against official sources (DOC, NZTA, local councils) |
| **Freshness** | Prices, hours, and access updated at least annually |
| **Specificity** | No generic content — every tip should contain concrete, actionable detail |
| **Tone** | Conversational, enthusiastic but honest. Match Buddi's persona. |
| **Length** | Pro tips: 1–3 sentences. Stories: 100–500 words. Area knowledge: 100–300 words. |
| **Attribution** | Source noted for every knowledge chunk |
| **Confidence** | Every chunk tagged `high`, `medium`, or `low` confidence |

### Quality Review Checklist

For each knowledge chunk:

- [ ] Is the information factually correct and current?
- [ ] Does it add value beyond what a quick Google search would reveal?
- [ ] Is it specific enough to act on? (Not "visit early" but "arrive before 7am")
- [ ] Is it sourced and attributed?
- [ ] Does it match Buddi's conversational tone?
- [ ] Is the confidence level appropriate?
- [ ] Are GPS coordinates accurate (verified on map)?
- [ ] Are condition dependencies correct (tested against real-world experience)?

### Automated Quality Checks

```python
class KnowledgeQualityChecker:
    def check_chunk(self, chunk: KnowledgeChunk) -> list[str]:
        issues = []

        if len(chunk.content) < 50:
            issues.append("Content too short — minimum 50 characters")
        if len(chunk.content) > 2000:
            issues.append("Content too long — maximum 2000 characters per chunk")
        if not chunk.source:
            issues.append("Missing source attribution")
        if not chunk.confidence:
            issues.append("Missing confidence level")
        if chunk.attraction_id and not self._attraction_exists(chunk.attraction_id):
            issues.append(f"Referenced attraction '{chunk.attraction_id}' does not exist")

        vague_phrases = ["visit early", "plan ahead", "check the weather", "it's beautiful"]
        for phrase in vague_phrases:
            if phrase in chunk.content.lower():
                issues.append(f"Contains vague phrase '{phrase}' — be more specific")

        return issues
```

## LLM-Generated vs Curated Content

### Strategy

The knowledge base uses a hybrid approach:

| Content Type | Source | Quality Gate |
|-------------|--------|-------------|
| **Attraction descriptions** | LLM-generated draft → human review | Must be reviewed before publishing |
| **Pro tips** | Human-curated only | Tips from personal experience, guides, DOC |
| **Stories** | LLM-generated from research sources → human review | Factual accuracy check required |
| **Area knowledge** | Mix — LLM for climate data, human for insights | Climate data auto-generated, insights curated |
| **Logistics** | LLM-generated from official sources → human verification | Prices, hours, and access must be verified |
| **Condition profiles** | Human-curated | Requires local/expert knowledge |

### LLM Content Generation Pipeline

```python
class KnowledgeGenerator:
    async def generate_attraction_draft(self, attraction_name: str, location: str) -> dict:
        prompt = f"""
        Generate a knowledge base entry for {attraction_name} near {location}, New Zealand.

        Include:
        1. A 2-3 sentence description of what it is and why it's worth visiting.
        2. Three specific pro tips (not generic advice — concrete, actionable tips
           with specific times, locations, or preparations).
        3. One 150-word story about the geological, cultural, or ecological significance.

        Requirements:
        - Be specific. "Arrive early" is not acceptable; "Arrive before 7am to get
          parking at the trailhead" is.
        - Include concrete details: distances, times, prices, specific locations.
        - Mark anything you're not confident about with [VERIFY].

        Format as JSON.
        """
        response = await self.llm.generate(prompt)
        draft = json.loads(response)
        draft["_status"] = "draft"
        draft["_generated_at"] = datetime.utcnow().isoformat()
        draft["_requires_review"] = True
        return draft
```

### Content Review Workflow

```
LLM generates draft
    ↓
Automated quality checks (length, specificity, format)
    ↓
Flagged items marked [VERIFY] highlighted for reviewer
    ↓
Human reviewer edits, verifies facts, adjusts tone
    ↓
Reviewer marks as "approved"
    ↓
Published to knowledge base
    ↓
Periodic re-review (annually or when flagged by users)
```

## Update Frequency and Freshness

### Freshness Requirements

| Content Type | Review Frequency | Trigger for Immediate Update |
|-------------|-----------------|------------------------------|
| Attraction descriptions | Annually | Major change (closure, new facility) |
| Prices and costs | Every 6 months | Price change detected |
| Opening hours | Every 6 months | Seasonal change |
| Pro tips | Annually | User reports inaccuracy |
| Stories | Rarely (unless incorrect) | Factual error discovered |
| Transport/logistics | Every 6 months | Road changes, new services |
| Condition profiles | Annually | Major infrastructure change |
| Seasonal calendars | Annually | Based on previous year data |

### Staleness Detection

```python
class FreshnessMonitor:
    FRESHNESS_THRESHOLDS = {
        "attraction": timedelta(days=365),
        "pro_tip": timedelta(days=365),
        "logistics": timedelta(days=180),
        "cost": timedelta(days=180),
        "story": timedelta(days=730),  # 2 years
    }

    def get_stale_content(self, destination_id: str) -> list[dict]:
        stale = []
        for chunk in self.get_all_chunks(destination_id):
            threshold = self.FRESHNESS_THRESHOLDS.get(chunk.type, timedelta(days=365))
            age = datetime.utcnow() - chunk.updated_at
            if age > threshold:
                stale.append({
                    "chunk_id": chunk.id,
                    "type": chunk.type,
                    "age_days": age.days,
                    "threshold_days": threshold.days,
                    "last_updated": chunk.updated_at.isoformat(),
                    "attraction": chunk.attraction_id,
                })
        return stale
```

## Scaling from NZ Pilot to Worldwide

### Phase 1: NZ Pilot (MVP)

- **Scope**: 8–10 NZ regions (Queenstown, Milford, Coromandel, Rotorua, Abel Tasman, Bay of Islands, Tongariro, Kaikōura, Wanaka, Dunedin)
- **Depth**: 15–30 attractions per region, fully curated
- **Content volume**: ~200 attractions, ~600 pro tips, ~200 stories, ~50 area chunks
- **Knowledge chunks**: ~1,500 total RAG chunks
- **Effort**: ~4 weeks of content creation for one person

### Phase 2: Expand NZ Coverage

- **Scope**: All major NZ travel regions (~20 regions)
- **Depth**: 15–30 attractions per region
- **Additional**: Secondary attractions, more transport links, freedom camping data
- **Content volume**: ~500 attractions, ~2,000 RAG chunks
- **Effort**: ~2 months, with LLM generation + human review

### Phase 3: Australia / Pacific Islands

- **Approach**: LLM generates base content; hire local reviewers for verification
- **New challenges**: Different API providers for tides, weather (BOM for Australia), wildlife species
- **Scale**: ~1,000 attractions, ~5,000 RAG chunks

### Phase 4: Worldwide

- **Approach**: Heavy LLM generation with crowdsourced review pipeline
- **Challenges**: Multiple languages, cultural sensitivity, vastly different infrastructure
- **Scale**: ~10,000+ attractions, ~50,000+ RAG chunks
- **Vector store**: Migrate from Chroma to Pinecone for scale

### Scaling Considerations

| Challenge | Solution |
|-----------|----------|
| Content creation speed | LLM-generated drafts reduce time to 30% of fully manual |
| Quality at scale | Automated quality checks + community review pipeline |
| Local accuracy | Regional reviewer network, user feedback loops |
| API differences by country | Adapter pattern (same interface, different implementations per region) |
| Language | Content in English first, i18n future phase |
| Vector store performance | Partition by region, use metadata filtering |
| Stale content detection | Automated freshness monitoring with review queue |

## Community Contribution Pipeline (Future)

### Vision

Travelers who use Journey Buddi can contribute back to the knowledge base:

1. **Trip reports**: After completing an activity, users can submit a short report.
2. **Tip contributions**: "I wish I'd known..." suggestions that become pro tips.
3. **Condition reports**: Real-world condition data that validates or corrects the knowledge base.
4. **Photo contributions**: User photos tagged to attractions (with permission).

### Moderation Flow

```
User submits contribution
    ↓
Automated screening (spam, inappropriate content, duplicates)
    ↓
LLM assessment (is this useful, specific, accurate-seeming?)
    ↓
Quality score assigned
    ↓
High-quality contributions → auto-approved (with human review queue)
Medium-quality → queued for human review
Low-quality → rejected with feedback
    ↓
Approved contributions added to knowledge base
    ↓
Contributor credited (optional gamification: "Local Expert" badge)
```

### Contribution Schema

```python
class UserContribution(BaseModel):
    user_id: str
    attraction_id: str
    contribution_type: str       # "tip", "correction", "condition_report", "photo"
    content: str
    visited_date: date
    conditions_observed: dict    # optional: weather, crowd level, etc.
    photos: list[str]            # optional: uploaded photo URLs
    submitted_at: datetime
    status: str                  # "pending", "approved", "rejected"
    quality_score: float         # 0-1, auto-assessed
    reviewer_notes: str          # if manually reviewed
```

## Vector Store Configuration

### Embedding Model

| Phase | Model | Dimensions | Reason |
|-------|-------|-----------|--------|
| MVP | `all-MiniLM-L6-v2` | 384 | Fast, lightweight, good for short chunks |
| Scale | `text-embedding-3-small` (OpenAI) or Gemini embeddings | 1536 | Better semantic quality at scale |

### Chunk Sizing

| Content Type | Target Chunk Size | Overlap |
|-------------|-------------------|---------|
| Pro tips | 1 tip per chunk (50–200 words) | None |
| Stories | 1 story per chunk (100–500 words) | None |
| Area knowledge | 1 topic per chunk (100–300 words) | None |
| Logistics | 1 topic per chunk (50–200 words) | None |

### Metadata for Filtering

Every chunk includes metadata for filtered retrieval:

```python
chunk_metadata = {
    "destination_id": "queenstown",
    "region": "otago",
    "attraction_id": "roys-peak",        # optional, if attraction-specific
    "chunk_type": "pro_tip",             # pro_tip, story, area_knowledge, logistics
    "category": "photography",           # timing, viewpoint, preparation, etc.
    "season_relevant": ["dec", "jan", "feb"],  # optional: seasonal relevance
    "confidence": "high",
    "source": "local guide",
    "updated_at": "2025-01-15",
}
```

This allows the AI agent to scope searches:
- "Find pro tips for Roy's Peak" → filter by `attraction_id` + `chunk_type`
- "What's the area like around Queenstown in winter?" → filter by `destination_id` + `season_relevant` contains `jun`

## Cross-References

- **Knowledge system design**: See [Knowledge System](../03-ai/KNOWLEDGE-SYSTEM.md)
- **How the AI agent retrieves knowledge**: See [AI Agent Overview](../03-ai/AI-AGENT-OVERVIEW.md)
- **Attraction data model**: See [Data Model](../05-architecture/DATA-MODEL.md)
- **Wildlife knowledge entries**: See [Wildlife Data](./WILDLIFE-DATA.md)
- **Prompt architecture for knowledge use**: See [Prompt Architecture](../03-ai/PROMPT-ARCHITECTURE.md)
- **Vector store infrastructure**: See [Tech Stack](../05-architecture/TECH-STACK.md)
