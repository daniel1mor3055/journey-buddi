# Itinerary Adaptation Engine

## Overview

The itinerary adaptation engine is the decision-making system that determines when and how to suggest changes to the traveler's plan. It balances the desire for optimal conditions against the friction of changing plans, producing suggestions only when the trade-off clearly favors adaptation.

## Core Philosophy

**"Better, not perfect."** We don't chase optimal conditions for every activity. We pursue meaningful improvements that justify the disruption of changing plans. A traveler who follows our original plan should still have a great trip. A traveler who accepts our adaptation suggestions should have an exceptional one.

## Adaptation Types

### Type 1: Day Swap
Swap two entire days when one day's activities are highly weather-sensitive and a better window exists.

**Example:**
- Day 7 (planned: Tongariro Crossing) has POOR conditions
- Day 10 (planned: Taupō lake activities) has EXCELLENT conditions
- Swap: Move Tongariro to Day 10, Taupō activities to Day 7

**Complexity: LOW** — Just reordering days, minimal logistics change.

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
