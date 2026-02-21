# Planning Phase — Detailed Specification

## Overview

The planning phase is where Journey Buddi's AI architect, Buddi, transforms a traveler's desires into a fully structured, geographically optimized, condition-aware itinerary. This phase happens entirely before the trip — typically days to weeks before departure.

The planning phase is designed as a **conversation, not a form**. Users don't fill out fields; they talk with Buddi, who guides them through structured decisions using concrete options.

## Planning Flow

```
[Landing] → [Quick Profile] → [Destination Selection] → [Interest Exploration]
     → [Attraction Curation] → [Route Building] → [Transport Selection]
     → [Pace & Duration] → [Itinerary Assembly] → [Review & Refine]
     → [Ready for Trip]
```

## Step 1: Quick Profile

### Purpose
Establish the traveler's identity and travel DNA in under 2 minutes.

### Interaction Design
Buddi presents a series of quick-choice cards (not open text):

**Adventure Level:**
- "Scenic viewpoints and easy walks" (Low)
- "Day hikes and kayaking" (Moderate)
- "Multi-day treks and extreme sports" (High)

**Physical Fitness:**
- "I prefer drives and short walks" (Low)
- "Comfortable with 3-4 hour hikes" (Moderate)
- "I can handle full-day strenuous hikes" (High)

**Travel Pace:**
- "I want downtime — 1-2 activities per day max" (Relaxed)
- "A good balance — 2-3 activities, some rest" (Balanced)
- "Pack it in — I want to see everything!" (Intensive)

**Interests** (multi-select with visual icons):
- Wildlife & Marine Life
- Mountains & Glaciers
- Beaches & Coast
- Lakes & Rivers
- Forests & Rainforests
- Volcanoes & Geothermal
- Stargazing & Aurora
- Photography & Scenery
- Water Sports (kayaking, surfing, diving)
- Hiking & Trekking
- Cultural & Historical Sites
- Food & Wine
- Unique Experiences (bungy, skydive, etc.)

**Budget for Activities:**
- "Budget-friendly — mostly free/cheap activities" (Low)
- "Happy to spend on key experiences" (Medium)
- "Money isn't the main concern" (High)

### Data Captured
```
UserProfile {
  adventure_level: low | moderate | high
  fitness_level: low | moderate | high
  pace: relaxed | balanced | intensive
  interests: string[]
  activity_budget: low | medium | high
}
```

## Step 2: Destination & Dates

### Purpose
Establish where and when the traveler is going.

### Interaction Design
- Destination selection (initially NZ only, expandable)
- Trip start date (calendar picker)
- Trip end date OR "flexible — Buddi can suggest duration"
- Arrival point (airport/city)
- Departure point (same or different)

### Smart Considerations
- Buddi should note seasonal implications: "You're traveling in July — that's winter in NZ. Some highland roads may be closed. I'll factor that into the plan."
- Regional sub-destination selection for large countries: "Would you like to explore both North and South Islands, or focus on one?"

## Step 3: Interest Exploration

### Purpose
Dive deeper into the selected interests with destination-specific context.

### Interaction Design
For each selected interest, Buddi presents concrete destination-specific options:

**Example — Wildlife & Marine Life in NZ:**
> "New Zealand has incredible wildlife! Here are some experiences I'd love to help you plan:"
> - 🐬 Swim with dolphins (Kaikoura, Akaroa, Bay of Islands)
> - 🐋 Whale watching (Kaikoura)
> - 🐧 Penguin colonies (Oamaru, Dunedin, Milford Sound)
> - 🦭 Seal colonies (Kaikoura, Abel Tasman, Milford Sound)
> - 🌌 Glowworm caves (Waitomo, Te Anau)
> - 🐦 Kiwi spotting (Stewart Island, Zealandia)
>
> "Which of these excite you? Select all that interest you."

**Example — Mountains & Glaciers in NZ:**
> "NZ's mountains and glaciers are world-class. Here's what's possible:"
> - 🏔️ Tongariro Alpine Crossing (full-day volcanic hike)
> - 🧊 Fox or Franz Josef Glacier (heli-hike or valley walk)
> - ⛰️ Mount Cook / Aoraki region (Hooker Valley, Mueller Hut)
> - 🏔️ Milford Sound (fiord cruise with mountain backdrop)
> - 🌋 White Island volcano (active volcano visit)
>
> "Given your moderate fitness level, all of these are within your range."

### Key Design Principle
**Every question has concrete options.** We never ask "what do you want to do?" We always present specific, curated choices. The user's job is to select, not to generate ideas.

## Step 4: Attraction Curation

### Purpose
For selected interests, determine specific locations and resolve conflicts.

### Interaction Design
When an activity is available at multiple locations, Buddi provides a recommendation:

> "Dolphin swimming is available in three spots along your route:"
> - **Kaikoura** — Dusky dolphins, high encounter rates (95%), fits naturally in a South Island east coast route
> - **Akaroa** — Hector's dolphins (world's rarest), beautiful harbor setting, near Christchurch
> - **Bay of Islands** — Bottlenose dolphins, warmer water, North Island
>
> "Based on your South Island focus, I'd recommend **Kaikoura** — it has the highest encounter rates and fits perfectly between Christchurch and Blenheim. But if seeing the rare Hector's dolphin matters to you, Akaroa is a worthy detour (2-hour drive from Christchurch)."
>
> "Which would you prefer? Or would you like to do both?"

### Smart Logic
- Buddi considers route impact when suggesting locations
- Never suggests something that requires massive detours without acknowledging the trade-off
- Groups nearby attractions ("Since you'll be in the Kaikoura area, you could also do whale watching and seal colony — all in one area")
- Flags seasonal availability ("White Island tours may be limited in winter")

## Step 5: Route Building

### Purpose
Assemble selected attractions into a geographically logical route.

### Logic
Buddi uses geographical clustering and route optimization to:
1. Group nearby attractions into "area clusters"
2. Determine logical route direction (clockwise vs. counterclockwise for NZ South Island, etc.)
3. Minimize backtracking while respecting "must-do" timing constraints
4. Account for ferry crossings, flights, and route bottlenecks

### Output
A high-level route skeleton:
```
Day 1-2: Christchurch arrival & Banks Peninsula
Day 3-4: Kaikoura (dolphins, whales, seals)
Day 5: Drive to Blenheim / Marlborough
Day 6-7: Abel Tasman (kayaking, walks)
Day 8: Drive to Punakaiki (Pancake Rocks)
Day 9-10: Glacier country (Fox/Franz Josef)
...
```

## Step 6: Transport & Logistics

See [TRANSPORT-LOGIC.md](./TRANSPORT-LOGIC.md) for detailed transport recommendation system.

## Step 7: Pace & Duration

### Purpose
Calibrate the itinerary density and determine total trip length.

### Interaction Design
Buddi presents the route with activity density and asks the user to validate:

> "Based on everything you've selected, I'd recommend **18 days** for the South Island:"
> - 2 activity-heavy days followed by 1 lighter day (matching your 'balanced' pace)
> - Average 1.5 hours of driving per day
> - 3 rest/exploration days built in for flexibility and spontaneous discovery
>
> "If you only have 14 days, here's what I'd suggest removing or combining: [options]"
> "If you could extend to 21 days, here's what we could add: [options]"

### Duration Flexibility
If the user has flexible dates, Buddi should confidently recommend duration. If dates are fixed, Buddi should optimize within constraints and transparently communicate trade-offs.

## Step 8: Itinerary Assembly

### Purpose
Generate the complete day-by-day itinerary with activities, transport, and timing.

### Output Structure
For each day:
```
Day {n}: {Area/Theme}
  Location: {where you'll be}
  Activities:
    - {Activity 1}: {description}, {estimated duration}
    - {Activity 2}: {description}, {estimated duration}
  Transport: {mode, distance, estimated time}
  Accommodation Zone: {area to find lodging}
  Notes: {any special considerations}
  Conditions That Matter: {what weather/conditions affect this day}
```

### Itinerary Intelligence
- No back-to-back strenuous days (unless user explicitly wants intensive pace)
- Weather-sensitive activities distributed across the trip (not all clustered)
- Long drives split with interesting stops
- Activities grouped by geography, not randomly scattered
- Morning activities for things that benefit from early starts
- Flexible slots for weather-dependent swaps

## Step 9: Review & Refine

### Purpose
User reviews the complete itinerary and makes adjustments.

### Capabilities
- View complete itinerary on map and as day-by-day list
- Tap any day to see details and Buddi's reasoning
- Drag to reorder days (Buddi validates feasibility: "Moving Milford Sound to day 3 adds 4 hours of driving — are you sure?")
- Add new activities (Buddi suggests where they fit best)
- Remove activities (Buddi re-optimizes surrounding days)
- Adjust pace for specific segments
- Lock specific days that shouldn't change (birthdays, bookings, etc.)

### Finalization
When the user is satisfied:
- Itinerary moves to "confirmed" state
- Buddi begins monitoring conditions for the trip dates
- Pre-trip preparation tips are generated
- The trip countdown begins

## Planning Phase Data Flow

```
User Input → Profile Engine → Interest Matcher → Attraction Curator
     → Route Optimizer → Transport Analyzer → Pace Calibrator
     → Itinerary Assembler → Review Interface → Confirmed Itinerary
```

Each step enriches the trip data object, and the AI agent has access to all accumulated context throughout the conversation.
