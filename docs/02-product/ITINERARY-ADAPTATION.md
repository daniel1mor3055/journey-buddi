# Itinerary Adaptation Engine

## Overview

The itinerary adaptation engine is the decision-making system that determines when and how to suggest changes to the traveler's plan. It balances the desire for optimal conditions against the friction of changing plans, producing suggestions only when the trade-off clearly favors adaptation.

## Core Philosophy

**"Better, not perfect."** We don't chase optimal conditions for every activity. We pursue meaningful improvements that justify the disruption of changing plans. A traveler who follows our original plan should still have a great trip. A traveler who accepts our adaptation suggestions should have an exceptional one.

**"Change only when it matters."** Itinerary changes are disruptive — they may require rebooking accommodation, rescheduling activities, contacting providers, and adjusting transport. We only recommend changes for conditions that truly ruin an experience (going to see aurora with no Kp-index, climbing Mount Cook in dangerous wind, kayaking in a storm). Minor imperfections (slightly cloudy for a viewpoint, light drizzle on a city walk) are NOT worth the disruption.

**"Look ahead, act early."** Users don't want to learn about a change on the morning of. The system should identify potential issues 2-5 days in advance (within forecast accuracy limits) so users have time to plan changes, make calls, and adjust logistics. Day-of changes should be rare and only for safety or dramatic condition shifts.

## Forecast Accuracy & Look-Ahead Windows

Not all conditions can be predicted with the same accuracy at the same range. The adaptation engine must factor forecast confidence into its decisions.

### Accuracy Windows by Condition Type

| Condition | Reliable Forecast Window | Max Useful Window | Notes |
|-----------|------------------------|-------------------|-------|
| Aurora (Kp-index, Bt/Bz) | 1-2 days | 3 days max | Solar wind data from ACE/DSCOVR satellites, Kp predictions highly volatile beyond 48h |
| Wind speed/direction | 2-3 days | 4 days | Mesoscale models (GFS, ECMWF) good at 48-72h, degrade after |
| Precipitation (rain/snow) | 3-4 days | 6 days | Synoptic-scale patterns predictable 3-4 days; intensity less certain |
| Cloud cover | 2-3 days | 5 days | Moderate reliability; local effects (marine layer, orographic) reduce accuracy |
| Temperature | 4-5 days | 7 days | Most predictable variable; trends reliable a week out |
| Tides | Weeks | Months | Astronomical, highly predictable — not a forecast concern |
| Wave height/swell | 2-3 days | 5 days | Swell models good at 48-72h; local wind-waves less certain |
| Road/trail closures | Real-time | Next day | Reactive, not forecast — depends on conditions |

### Confidence Scoring

Every condition score includes a confidence level:
- **High confidence** (within reliable window): "Tuesday will be excellent for Tongariro — clear skies, light winds."
- **Medium confidence** (within max useful window): "Thursday is looking promising for kayaking, but wind forecasts could shift."
- **Low confidence** (beyond useful window): "Next Monday's conditions can't be reliably predicted yet. I'll update you as we get closer."

### Decision Impact

Confidence affects adaptation decisions:
- **High confidence + poor conditions** → Strong swap recommendation
- **Medium confidence + poor conditions** → Gentle suggestion, monitor and update
- **Low confidence** → No action, flag for future monitoring only
- NEVER recommend a major itinerary change based on low-confidence forecasts

### Forecast Integrations

| Source | Data | Update Frequency |
|--------|------|-----------------|
| OpenWeatherMap API | General weather | Hourly |
| ECMWF (European Centre) | Premium forecast models | Every 6 hours |
| Windy.com / Windguru | Wind-specific, marine data | Hourly |
| NOAA SWPC | Aurora/solar activity (Kp, Bt, Bz) | Every 15 minutes |
| LINZ / NIWA | NZ tides | Daily |
| MetService NZ | NZ-specific weather, severe warnings | Hourly |
| DOC (Dept of Conservation) | Trail/road closures | As updated |
| Agent web search | Fallback for any missing/niche data | On demand |

The system should prefer structured APIs but fall back to agent web search when API data is unavailable or for niche conditions (e.g., glacial river levels, specific volcanic activity).

## Adaptation Types

### Type 1: Day Swap
Swap two entire days when one day's activities are highly weather-sensitive and a better window exists.

**Example:**
- Day 7 (planned: Tongariro Crossing) has POOR conditions
- Day 10 (planned: Taupō lake activities) has EXCELLENT conditions
- Swap: Move Tongariro to Day 10, Taupō activities to Day 7

**Complexity: LOW** — Just reordering days, minimal logistics change.

**Geographic Smoothness Rule:**
Swaps must not create back-and-forth travel patterns. If swapping Day 7 and Day 10 means driving 3 hours south on Day 7, then 3 hours north on Day 8, then south again on Day 9 — it's not worth it regardless of condition improvement. Swaps must respect geographic flow. The best swaps are between days in the same area or adjacent areas.

### Type 2: Activity Rescheduling
Move a specific activity to a different day within the same area cluster.

**Example:**
- Morning kayak on Day 5 has HIGH wind
- Day 6 morning has calm conditions
- Move kayak from Day 5 morning to Day 6 morning
- Fill Day 5 morning with a wind-resistant activity from Day 6

**Complexity: MEDIUM** — Requires rebalancing activities across days.

### Type 3: Alternative Substitution
Replace a weather-impacted activity with an alternative that works in current conditions.

**Example:**
- Outdoor scenic helicopter flight cancelled due to fog
- Suggest: Underground glowworm cave tour nearby (unaffected by weather)
- The helicopter flight can be attempted later if conditions improve

**Complexity: MEDIUM** — Requires knowledge of alternatives in the area.

### Type 4: Timing Shift
Adjust the timing of an activity within the same day to hit a weather window.

**Example:**
- Afternoon coastal walk planned, but rain expected from 2 PM
- Shift to morning walk (10 AM), move morning activity to afternoon (it's indoor)

**Complexity: LOW** — Same day, same activities, different order.

### Type 5: Extended Stay / Skip Forward
When conditions are so good or bad that spending more or less time in an area makes sense.

**Example:**
- Exceptional clear weather in Mount Cook region (rare, only 30% of days are clear)
- Suggest: Stay an extra day, do the Mueller Hut track or Tasman Glacier walk
- Compress time in the next area (which has rain coming anyway)

**Complexity: HIGH** — Changes trip structure, potentially affects accommodation.

## Decision Process

### Step 1: Daily Condition Scan

Every day at T-18h and T-6h, the engine:
1. Fetches updated conditions for today's and next 4 days' activities
2. Scores each activity's conditions
3. Identifies any activities scoring FAIR or below

### Step 2: Swap Opportunity Detection

For each underperforming activity:
1. Check if the same activity scores better on another day within the trip
2. Check if the day it would move from has a compatible alternative
3. Evaluate what activity currently on the "better" day would move to the "worse" day
4. Confirm the moved activity is weather-resistant enough for the worse conditions

### Step 3: Impact Assessment

For each potential swap:

```
ImpactAssessment {
  condition_improvement: {
    original_score: 35,        // POOR
    swapped_score: 88,         // EXCELLENT
    delta: +53                 // Significant improvement
  }
  displaced_activity_impact: {
    original_score: 75,        // GOOD in its original slot
    new_score: 60,             // Still GOOD in the swapped slot
    delta: -15                 // Minor degradation, acceptable
  }
  logistics: {
    additional_driving_km: 0,
    additional_driving_minutes: 0,
    accommodation_change_needed: false,
    booking_conflicts: [],
    route_deviation: "none"
  }
  user_effort: {
    changes_required: 1,       // Number of days affected
    complexity: "low",         // How hard is this to execute?
    explanation_clarity: "high" // Can we explain this simply?
  }
}
```

### Step 4: Decision Threshold

```
improvement = condition_improvement.delta - abs(displaced_activity_impact.delta)
disruption = user_effort.complexity_score + logistics.total_impact_score

IF improvement > 40 AND disruption < 30:
  → STRONG RECOMMENDATION (proactive notification)
  
ELIF improvement > 25 AND disruption < 50:
  → SUGGESTION (included in morning briefing)
  
ELIF improvement > 15 AND disruption < 20:
  → MENTION (brief note in briefing, easy to ignore)
  
ELSE:
  → NO ACTION
```

### Step 5: Suggestion Generation

The AI agent generates a human-readable explanation:

**Required elements:**
1. What's the problem with the current plan
2. What's the proposed change
3. Why the alternative day/time is better
4. What happens to the displaced activity
5. What the user needs to do (step by step)
6. What stays the same (reassurance)

### Step 5b: Comprehensive Change Instructions

When a swap is accepted, the user must receive a COMPLETE action plan with NO loose ends. This is critical — a half-baked change plan is worse than no plan.

**The Change Action Plan includes:**

1. **What changes automatically** (Buddi handles these):
   - Itinerary day reordering
   - Activity rescheduling within days
   - Transport recalculation (new routes, distances, times)
   - Updated packing lists and condition forecasts
   - New Google Maps links and directions

2. **What the user needs to do** (explicit, step-by-step):
   - Accommodation changes: "You need to call [Hotel Name] at [phone] to move your check-in from Dec 12 to Dec 14. Their cancellation policy allows free changes up to 48h before."
   - Activity rebooking: "Contact [Provider Name] to reschedule your dolphin swim from Tuesday to Thursday morning. Their number is [phone] or rebook at [URL]. Mention booking ref [REF]."
   - Transport adjustments: "Your rental car pickup is still from the same location, but you'll now drive north first instead of south. Updated route is in your Google Maps."

3. **Timeline for making changes:**
   - Which calls/actions are time-sensitive (do today)
   - Which can wait (anytime before the affected day)
   - Which are optional nice-to-haves

4. **Fallback if changes can't be made:**
   - "If [Hotel Name] can't accommodate the date change, here are 3 alternatives in the same area: [options]"
   - "If the dolphin swim is fully booked for Thursday, Wednesday afternoon also works — here's the revised schedule for that."

5. **What stays the same** (reassurance):
   - "Days 1-6 and Days 11-18 are completely unchanged."
   - "Your Milford Sound cruise on Day 15 is unaffected."
   - "Your flights remain the same."

**Principle: The user should be able to execute the change by following the instructions like a checklist. Zero ambiguity, zero loose ends.**

## Swap Constraints

### Hard Constraints (Never violate)
- Don't swap locked days (user has bookings or personal reasons)
- Don't create impossible logistics (16-hour drive day)
- Don't swap activities that have non-refundable bookings
- Don't suggest more than 2 active swap suggestions at once
- Don't re-suggest a swap the user has already declined

### Soft Constraints (Try to respect)
- Minimize cascading changes (prefer swapping 2 days over restructuring 5)
- Preserve rest day positioning
- Maintain geographic logic (don't create backtracking)
- Respect the trip's narrative arc (don't move the "climax" activity to day 1)
- Don't suggest swaps for the current day after 10 AM (too late, user is already in motion)

## Handling User Responses

### User Accepts
1. Update the itinerary immediately
2. Confirm the change with a summary
3. Regenerate affected day briefings
4. Update condition monitoring for the new arrangement

### User Declines
1. Respect the decision without argument
2. Record the decline to avoid re-suggesting
3. Provide tips to make the best of suboptimal conditions
4. "No problem! Here's how to make the most of Tongariro in cloudy conditions: [tips]"

### User Asks for More Info
1. Provide detailed condition comparison between the two days
2. Show forecast confidence levels
3. Explain the displaced activity's condition resilience
4. Offer to modify the suggestion

## Adaptation Learning

Over time, the system tracks:
- What types of swaps users accept vs. decline
- Which condition thresholds users care about most
- Whether accepted swaps resulted in better experiences (post-trip feedback)
- Patterns that can improve future threshold calibration

## Smart Look-Ahead Process

The adaptation engine uses a rolling look-ahead window that considers forecast accuracy:

### Daily Assessment Cycle

1. **T-5 to T-7 days**: Temperature and general trend monitoring only. No action, just flagging potential concerns. "Heads up: Day 12 might see some weather — I'm monitoring."

2. **T-3 to T-5 days**: Rain, cloud, and wind patterns become actionable. If a high-sensitivity activity (like Tongariro Crossing) shows POOR on a day where another nearby day shows GOOD, begin formulating a swap plan. Communicate to user: "I'm seeing a potential issue with Day 9 and have a plan ready if it holds."

3. **T-2 to T-3 days**: Most conditions are reliable. This is the OPTIMAL window for swap decisions — early enough for the user to act (rebook accommodation, contact providers) but late enough for accurate forecasts.

4. **T-1 day**: Confirm or adjust. Evening briefing includes final assessment. Same-day changes should be rare (only safety or dramatic shifts).

5. **T-0 (day of)**: Real-time monitoring only. No proactive swaps after 10 AM — the user is already executing. Safety alerts are the exception.

### Multi-Day Shuffle Illustration

When a swap involves rearranging 2-3 days (not just swapping two), the engine must present it as a single coherent plan:

**Before:**
| Day 7 (Mon) | Day 8 (Tue) | Day 9 (Wed) |
|-------------|-------------|-------------|
| Kayaking 🔴 | Museum + Town 🟡 | Hike to Hut 🟢 |

**After (suggested):**
| Day 7 (Mon) | Day 8 (Tue) | Day 9 (Wed) |
|-------------|-------------|-------------|
| Museum + Town 🟡 | Hike to Hut 🟢 | Kayaking 🟢 |

**Why this works:**
- Monday's high wind ruins kayaking but doesn't affect indoor activities
- Moving the hike one day earlier still has good conditions
- Wednesday's forecast shows calm winds perfect for kayaking
- All three days are in the same area — no extra driving needed
- Accommodation stays the same for all three nights

**What the user needs to do:**
- Call kayak provider to move from Monday to Wednesday: [phone/link]
- The hut booking is flexible — no change needed
- Everything else stays the same

## Edge Cases

### Everything Is Bad
When weather is poor for the entire remaining trip:
- Acknowledge it honestly: "The forecast isn't great for the next few days"
- Suggest weather-resistant activities in the area
- Identify the least-bad day for weather-sensitive activities
- Reassure: "Some of NZ's most dramatic moments happen in moody weather"

### Everything Is Great
When all conditions are excellent:
- Reinforce confidence: "You've hit a perfect weather window!"
- Suggest optional enhancements (longer hike variant, side trips)
- No adaptation needed — let the user enjoy the plan

### Cascading Changes
When one swap triggers the need for another:
- Present as a single, coherent plan change (not a cascade of individual swaps)
- Limit cascading to 3 affected days maximum
- If more would cascade, consider a partial restructure instead

### Last-Minute Condition Shift
When conditions change after the morning briefing:
- Only alert for changes to current/immediate next activity
- For safety concerns, alert immediately
- For quality concerns, note it but don't push hard — the user is already executing
