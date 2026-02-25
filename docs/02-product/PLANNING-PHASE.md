# Planning Phase — Detailed Specification

## Overview

The planning phase is where Journey Buddi's AI architect, Buddi, transforms a traveler's desires into a fully structured, geographically optimized, condition-aware itinerary. This phase happens entirely before the trip — typically days to weeks before departure.

The planning phase is designed as a **conversation, not a form**. Users don't fill out fields; they talk with Buddi, who guides them through structured decisions using concrete options.

## Planning Flow

```
[Landing] → [Quick Profile] → [Destination Selection] → [Priority Locations]
     → [Interest Exploration] → [Attraction Curation] → [Route Building]
     → [Transport Selection] → [Pace & Duration] → [Itinerary Assembly]
     → [Review & Refine] → [Ready for Trip]
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
- "I prefer drives and short walks — flat paths, up to 30 minutes" (Low)
- "Comfortable with moderate hikes — 3-4 hours with some elevation, like Hooker Valley Track" (Moderate)
- "I can handle full-day strenuous hikes — 8+ hours, steep terrain, like Tongariro Alpine Crossing" (High)

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

**Travel Group:**
- "Flying solo — just me and the open road" (Solo)
- "With my partner — adventure for two" (Couple)
- "Family trip — kids are coming along" (Family)
- "Friends trip — the crew is rolling deep" (Friends Group)

### Data Captured
```
UserProfile {
  adventure_level: low | moderate | high
  fitness_level: low | moderate | high
  pace: relaxed | balanced | intensive
  interests: string[]
  activity_budget: low | medium | high
  travel_group: solo | couple | family | friends
  max_driving_hours_per_day: number  // User's preferred max
  priority_locations: string[]       // Must-visit places
  flight_details: { arrival: FlightInfo, departure: FlightInfo }
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
- Maximum driving hours per day preference:
  - "1-2 hours max — I'm here for the stops, not the driving" (Light)
  - "3-4 hours is fine — road trips are part of the fun" (Moderate)
  - "5+ hours if needed — I want to cover ground" (Heavy)
- Flight details collection (airline, flight number, arrival/departure time) — used for Day 1 and final day logistics so Buddi can plan around actual arrival and departure windows
- Buddi recommends the optimal number of days based on destination, selected interests, and travel pace — if the user has flexible dates, Buddi confidently suggests duration with reasoning

### Smart Considerations
- Buddi should note seasonal implications: "You're traveling in July — that's winter in NZ. Some highland roads may be closed. I'll factor that into the plan."
- Regional sub-destination selection for large countries: "Would you like to explore both North and South Islands, or focus on one?"
- **Seasonal intelligence**: Buddi explains what's best in the traveler's season, what's unavailable, and what to expect. If dates are flexible, Buddi actively suggests the best travel window with reasons (e.g., "March is shoulder season — fewer crowds, autumn colors in Arrowtown, but some highland tracks may close early").

## Step 3: Priority Locations & Must-Dos

### Purpose
Identify non-negotiable destinations or experiences before building the itinerary. These become locked constraints that the route optimizer must respect.

### Interaction Design
Buddi asks if there are any must-visit places or must-do activities:

> "Before I start building your route — are there any places or experiences that are absolutely non-negotiable for you? Things you'd be disappointed to miss?"

The user can:
- Select from popular suggestions for the destination
- Type their own must-dos in natural language
- Say "no strong feelings — surprise me, Buddi!"

Buddi also asks for "must-not-dos" — things the user explicitly wants to avoid:

> "Anything you definitely DON'T want? Some people hate long boat rides, others avoid heights. No judgment — just tell me."

### Constraint Handling
- Must-do locations and activities become **locked constraints** in the route optimizer
- Must-not-dos are added to a rejection list and filtered out of all recommendations
- User overrides are sacred. If the user has a must-do or must-not-do, Buddi must respect it absolutely — the client is always right.

## Step 4: Interest Exploration

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

## Step 5: Attraction Curation

### Purpose
For selected interests, determine specific locations and resolve conflicts. The key principle is **geographic diversification** — travelers want highlights spread across their entire trip, not bunched in one spot. Buddi compares providers across ALL of New Zealand, not just the current route location.

### Interaction Design
When an activity is available at multiple locations, Buddi provides a recommendation with provider intelligence across the entire destination:

> "Dolphin swimming is available in three spots along your route:"
> - **Kaikoura** — Dusky dolphins, high encounter rates (95%), fits naturally in a South Island east coast route
> - **Akaroa** — Hector's dolphins (world's rarest), beautiful harbor setting, near Christchurch
> - **Bay of Islands** — Bottlenose dolphins, warmer water, North Island
>
> "Based on your South Island focus, I'd recommend **Kaikoura** — it has the highest encounter rates and fits perfectly between Christchurch and Blenheim. But if seeing the rare Hector's dolphin matters to you, Akaroa is a worthy detour (2-hour drive from Christchurch)."
>
> "Which would you prefer? Or would you like to do both?"

**Nationwide provider comparison example — Adventure Activities:**

> "Let's look at skydiving options across New Zealand:"
> - **Queenstown (Nzone Skydive)** — 15,000ft, dramatic mountain and lake backdrop, consistently rated #1 in NZ. ⭐ 4.9 TripAdvisor. $349 NZD
> - **Wanaka (Skydive Wanaka)** — 15,000ft, views of Mt Aspiring and Lake Wanaka, less crowded than Queenstown. ⭐ 4.8 TripAdvisor. $339 NZD
> - **Taupō (Skydive Taupo)** — 15,000ft, views over Lake Taupō and volcanic plateau, great North Island option. ⭐ 4.7 TripAdvisor. $329 NZD
> - **Abel Tasman (Skydive Abel Tasman)** — 16,500ft (highest in NZ!), coastal views over golden beaches. ⭐ 4.8 TripAdvisor. $399 NZD
>
> "I'd recommend spreading your adrenaline activities across the trip — skydiving in Wanaka for the mountain views, bungy in Queenstown (the original AJ Hackett!), and perhaps paragliding in Kaikoura for coastal scenery. This way each day has its own highlight rather than doing everything in one spot."
>
> "What feels right to you? Or should I pick the best combination based on your route?"

### Curation Principles

- **Diversification Principle**: Spread highlights across the entire trip geographically. Don't cluster all adventure in Queenstown or all wildlife in Kaikoura.
- **Provider Intelligence**: For each activity type, show 2-3 best providers across NZ with: reviews (TripAdvisor/GetYourGuide ratings), price, unique differentiator (what makes THIS provider's experience special — better views? longer duration? rare species?), and a short Buddi recommendation.
- **Data Sources**: Buddi integrates with TripAdvisor, GetYourGuide, and destination tourism APIs for provider data. The agent can also search the web for new/updated provider information. Future: build our own booking database for direct booking through Journey Buddi.
- **"Just let Buddi decide" fallback**: When the user says "just pick the best" or "you decide", Buddi makes the call with clear reasoning.

### Smart Logic
- Buddi considers route impact when suggesting locations
- Never suggests something that requires massive detours without acknowledging the trade-off
- Groups nearby attractions ("Since you'll be in the Kaikoura area, you could also do whale watching and seal colony — all in one area")
- Flags seasonal availability ("White Island tours may be limited in winter")

## Step 6: Route Building

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

## Step 7: Transport & Logistics

See [TRANSPORT-LOGIC.md](./TRANSPORT-LOGIC.md) for detailed transport recommendation system.

## Step 8: Pace & Duration

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

## Step 9: Itinerary Assembly

### Purpose
Generate the complete day-by-day itinerary with activities, transport, and timing.

The itinerary output is NOT a chat message. It is an interactive dashboard — a control panel where the user can see every detail of their trip, check booking statuses, edit activities, view maps, and manage their journey. Think GetYourGuide's trip pages, not a text dump.

### Output Structure
For each day:
```
Day {n}: {Area/Theme}
  Location: {where you'll be}
  Google Maps: {link to location}
  Accommodation:
    Type: {hotel | motel | Airbnb | campervan | motorhome}
    Name: {property name}
    Address: {full address}
    Booking Status: {not booked | booked}
    Check-in: {time}
    Check-out: {time}
    Cost: {per night}
  Activities:
    - {Activity 1}: {description}, {estimated duration}
      Booking: {not booked | booked — time, confirmation #}
    - {Activity 2}: {description}, {estimated duration}
      Booking: {not booked | booked — time, confirmation #}
  Transport: {mode, distance, estimated time}
  Travel Distance: {total km for the day}
  Travel Duration: {total driving/transit time}
  Day Tightness: {relaxed | comfortable | tight | overpacked}
  What to Pack: {day-specific packing notes}
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

## Step 10: Review & Refine

### Purpose
User reviews the complete itinerary and makes adjustments. The itinerary is Buddi's expert recommendation, but the user has full control. They can accept 100% of it or rebuild 50% of it — the system adapts either way.

### Capabilities
- View complete itinerary on map and as day-by-day list
- Tap any day to see details and Buddi's reasoning
- Drag to reorder days (Buddi validates feasibility: "Moving Milford Sound to day 3 adds 4 hours of driving — are you sure?")
- Add new activities (Buddi suggests where they fit best)
- Remove activities (Buddi re-optimizes surrounding days)
- Adjust pace for specific segments
- Lock specific days that shouldn't change (birthdays, bookings, etc.)
- Users can add, remove, reorder, and edit ANY aspect of any day
- The UI must make editing effortless — not just possible, but inviting
- Buddi re-validates and re-optimizes after every user change

### Finalization
When the user is satisfied:
- Itinerary moves to "confirmed" state
- Buddi begins monitoring conditions for the trip dates
- Pre-trip preparation tips are generated
- The trip countdown begins

## Smart Question Design

Not every question needs an explicit answer. For questions where the user would struggle to articulate preferences (e.g., optimal day structure, activity sequencing), Buddi should offer to decide autonomously: "I'll optimize this based on your profile — or would you like to weigh in?"

### Design Principles

- **Multi-choice with visual cues wherever possible** — never expect the user to write paragraphs about their preferences
- **Flexible input**: Let users select from options OR type natural language OR say "you decide"
- **Progressive refinement**: Start with broad strokes, refine through follow-up only when needed
- **Effortless planning**: The planning conversation should feel effortless — 80-90% of the itinerary is agent-generated, the user's job is to validate, tweak, and get excited

### Common Autonomous Decision Points
- Optimal day structure and activity sequencing
- Which provider to choose when differences are marginal
- Rest day placement
- Route direction (clockwise vs counterclockwise)
- Activity timing within a day
- Driving route selection between two points

For all of these, Buddi should default to making the call with a brief explanation, and the user can override at any time during review.

## Planning Phase Data Flow

```
User Input → Profile Engine → Interest Matcher → Attraction Curator
     → Route Optimizer → Transport Analyzer → Pace Calibrator
     → Itinerary Assembler → Review Interface → Confirmed Itinerary
```

Each step enriches the trip data object, and the AI agent has access to all accumulated context throughout the conversation.
