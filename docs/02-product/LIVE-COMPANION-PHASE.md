# Live Companion Phase — Detailed Specification

## Overview

The live companion phase activates when the trip begins. This is where Journey Buddi transforms from a planning tool into an active travel partner. The static itinerary becomes a living system that monitors conditions, adapts plans, and provides expert-level guidance for each activity in real time.

This is the phase that truly differentiates Journey Buddi from everything else on the market.

## Phase Activation

The live companion activates based on the trip start date:

- **T-3 days**: Buddi begins monitoring weather forecasts for the first week of the trip
- **T-1 day**: Buddi sends a pre-departure briefing with arrival day details and first few days overview
- **T-0 (Trip Start)**: Full companion mode activates — daily briefings, condition monitoring, and adaptive suggestions begin

## Daily Rhythm

The live companion follows a natural daily rhythm aligned with how travelers actually experience their days:

### Evening Before (8:00 PM local time — configurable)
**"Tomorrow's Preview"**
- Brief overview of tomorrow's planned activities
- Early condition assessment for tomorrow
- Packing preparation reminder ("Pack your hiking boots and rain jacket for tomorrow's Hooker Valley walk")
- Departure time suggestion for the morning
- Any bookings or reservations to be aware of

### Morning (7:00 AM local time — configurable)
**"Today's Briefing" — The Core Daily Interaction**
- Full condition report for today's activities
- Go/adjust recommendation with confidence level
- Detailed packing list for the day
- Timing guidance for each activity
- Pro tips and hidden gems for today's locations
- If applicable: swap suggestion with reasoning

### During the Day (As Needed)
**"Live Updates"**
- Significant weather changes affecting current/upcoming activity
- Timing reminders ("Head to Cathedral Cove now to catch low tide at 2:30 PM")
- Spontaneous suggestions based on current conditions ("The clouds just cleared over Mt Cook — great time for photos if you're nearby!")

### Evening (After last activity)
**"Day Wrap & Tomorrow Prep"**
- Summary of what was experienced
- Any adjustments needed for tomorrow based on today's events
- Preview of next day's plan

## Condition Assessment

For each planned activity, Buddi evaluates conditions on a scale:

```
🟢 EXCELLENT — Perfect conditions for this activity, go for it!
🟡 GOOD — Conditions are solid, minor imperfections that won't impact enjoyment  
🟠 FAIR — Activity is doable but not ideal; consider if a better day exists
🔴 POOR — Conditions will significantly diminish the experience; strong swap recommended
⛔ UNSAFE — Conditions make this activity dangerous; do NOT proceed
```

### Assessment Factors by Activity Type

**Hiking/Trekking:**
- Wind speed and gusts (especially alpine/exposed trails)
- Precipitation (rain, snow)
- Temperature (including wind chill)
- Visibility/cloud cover (for viewpoint-dependent hikes)
- Trail conditions (recent heavy rain = mud/flooding)

**Water Activities (kayaking, swimming, surfing):**
- Wind speed and direction
- Wave height and swell
- Water temperature
- Tide times and levels
- Rainfall (affects visibility in water)

**Wildlife Viewing:**
- Time of day (species-specific activity windows)
- Tide level (affects coastal wildlife)
- Wind (affects bird activity, boat stability)
- Season (breeding, migration, feeding patterns)
- Moon phase (affects nocturnal wildlife)

**Scenic/Photography:**
- Cloud cover (clear for mountain/crater views, dramatic for some landscapes)
- Light conditions (golden hour, blue hour, harsh midday)
- Rain/mist (some scenes are enhanced by weather)
- Visibility distance
- Air quality

**Geothermal/Volcanic:**
- Wind direction (affects steam/gas drift)
- Rain (can enhance or diminish geothermal features)
- Temperature (extreme cold affects visitor comfort at outdoor geothermal areas)

## Swap Suggestion Logic

### When to Suggest a Swap

Buddi suggests itinerary changes ONLY when:

1. **Meaningful improvement**: Swapping demonstrably improves the experience (not just marginal gains)
2. **Feasible logistics**: The swap doesn't create cascading problems (impossible drives, missed bookings)
3. **Clear reasoning**: Buddi can articulate exactly why the swap helps
4. **User hasn't rejected similar swaps**: Respect the user's decision patterns

### When NOT to Suggest a Swap

- Minor condition variations ("3°C cooler than ideal" — not worth the disruption)
- Activities that are enjoyable in most conditions (Milford Sound in rain is stunning)
- When no better alternative exists for the swap day
- When the user has locked a day (bookings, personal reasons)
- Excessive swapping (max 2-3 swap suggestions per trip unless conditions are extreme)

### Swap Presentation Format

```
Buddi: "Hey! I've been checking tomorrow's conditions and I have a suggestion:

       📅 TOMORROW (Day 7 — Thursday):
       Current plan: Tongariro Alpine Crossing
       Conditions: 🔴 POOR — Wind gusts 65km/h at summit, low cloud, rain showers
       
       📅 PROPOSED SWAP with Day 9 (Saturday):
       Saturday's forecast: 🟢 EXCELLENT — Clear skies, light winds (15km/h), 
       perfect visibility of all volcanic craters
       
       Instead, tomorrow you could do:
       🎯 Huka Falls & Craters of the Moon (Taupō) — both are great in any 
       weather and you'll be in the area anyway
       
       What this means logistically:
       • Tomorrow: Stay in Taupō area, easy day with 2 short activities
       • Friday (Day 8): Continue as planned (Rotorua geothermal)
       • Saturday (Day 9): Do the Tongariro Crossing in perfect conditions
       • This adds a 45-minute drive on Saturday morning but the conditions 
         are worth 10x that
       
       [Accept swap — update my itinerary]
       [Keep original plan — I'll brave it]
       [Tell me more about the alternative day]"
```

### Swap Decision Inputs

```
SwapDecision {
  original_day: Day
  original_conditions: ConditionReport
  candidate_swap_day: Day  
  candidate_conditions: ConditionReport
  improvement_score: number (0-100)  // How much better is the swap?
  logistics_impact: {
    added_driving_minutes: number
    accommodation_changes_needed: boolean
    booking_conflicts: Booking[]
    cascading_day_changes: number
  }
  user_disruption_score: number (0-100)  // How much hassle for the user?
  recommendation: "strong_swap" | "suggest_swap" | "mention_option" | "no_action"
}
```

**Decision thresholds:**
- `improvement_score > 70` AND `user_disruption_score < 40` → Strong swap recommendation
- `improvement_score > 50` AND `user_disruption_score < 60` → Gentle suggestion
- `improvement_score > 30` AND `user_disruption_score < 30` → Mention as option
- Otherwise → No action

## Activity Guidance Detail

For each activity on a given day, Buddi provides comprehensive guidance. See [ACTIVITY-GUIDANCE.md](./ACTIVITY-GUIDANCE.md) for the full specification of what guidance includes and how it's generated.

## Multi-Day Lookahead

Buddi doesn't just look at today — it evaluates the next 3-5 days to find optimal windows:

```
Lookahead Analysis:
  Day 7 (Thu): Tongariro — POOR conditions
  Day 8 (Fri): Rotorua — GOOD (geothermal doesn't care about weather much)
  Day 9 (Sat): Taupō activities — GOOD  
  Day 10 (Sun): Lake Taupō & drive — FAIR
  Day 11 (Mon): Tongariro — EXCELLENT ← Best window!
  
  Recommendation: If flexible, move Tongariro to Day 11. 
  This means extending Taupō/Rotorua by 2 days, but both have enough 
  content to fill the time richly.
```

## Emergency & Safety Features

Beyond optimization, the live companion has safety responsibilities:

- **Severe weather alerts**: Immediate notification for storms, floods, extreme heat/cold
- **Activity closure notifications**: Trail closures, road closures, volcanic alerts
- **Alternative planning**: When a planned activity becomes impossible, immediately suggest alternatives
- **Local emergency information**: Nearest hospital, emergency services, embassy contacts
- **Travel advisories**: Government-issued warnings for the destination

## Offline Consideration (Future)

While offline mode is not in scope for V1, the architecture should support future offline capability:
- Cache today's and tomorrow's briefing for offline access
- Cache map data for the current area
- Queue condition checks for when connectivity returns
- Core itinerary data stored locally for reference
