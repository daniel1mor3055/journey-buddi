# AI Decision Engine

## Overview

The decision engine is the reasoning core of Buddi's intelligence. It evaluates conditions against activity requirements, weighs trade-offs, and produces recommendations. This document describes the decision-making framework used across all of Buddi's intelligent features.

## Decision Domains

### 1. Attraction Selection Decisions

**Question:** "Should I recommend this attraction to this user?"

**Inputs:**
- User profile (interests, fitness, pace, budget)
- Attraction attributes (type, difficulty, cost, duration, location)
- Route context (is it on the way or a detour?)
- Seasonal availability
- User's selected interests

**Logic:**
```
score = 0

# Interest match (40% weight)
if attraction.type in user.interests:
    score += 40 * interest_strength(attraction.type, user.interests)

# Fitness compatibility (20% weight)
if attraction.difficulty <= user.fitness_level:
    score += 20
elif attraction.difficulty == user.fitness_level + 1:
    score += 10  # Slightly challenging, flag it

# Route fit (20% weight)
detour_minutes = calculate_detour(attraction.location, current_route)
if detour_minutes == 0:
    score += 20  # On the route
elif detour_minutes < 30:
    score += 15  # Minor detour
elif detour_minutes < 60:
    score += 8   # Moderate detour
else:
    score += 2   # Significant detour, only if very high interest

# Budget fit (10% weight)
if attraction.cost_level <= user.budget:
    score += 10

# Uniqueness/special factor (10% weight)
score += attraction.uniqueness_score * 0.1

return score  # 0-100
```

Attractions scoring above 60 are recommended. 40-60 are mentioned as options. Below 40 are omitted unless the user specifically asks.

### 2. Location Selection Decisions

**Question:** "When the same activity is available at multiple locations, which one should I recommend?"

**Inputs:**
- Quality/experience rating at each location
- Route proximity for each location
- Crowd levels at each location
- Seasonal factors at each location
- Unique differentiators

**Logic:**
```
for each location offering the activity:
    location_score = (
        quality_rating * 0.35 +
        route_proximity_score * 0.25 +
        crowd_score * 0.15 +
        seasonal_score * 0.15 +
        uniqueness_bonus * 0.10
    )
```

Present the top recommendation with reasoning, and mention alternatives for the user to choose.

### 3. Route Optimization Decisions

**Question:** "What order should the clusters be visited?"

**Inputs:**
- Cluster locations (lat/lon centroids)
- Entry and exit points
- Inter-cluster drive times
- Seasonal/directional preferences (some routes are better clockwise vs. counterclockwise)
- Fixed date constraints (bookings, events)

**Algorithm:**
1. Generate feasible route permutations (entry → clusters → exit)
2. Filter out routes violating hard constraints
3. Score remaining routes:
   ```
   route_score = (
       -total_drive_time * 0.4 +          # Minimize driving
       -backtracking_penalty * 0.3 +       # Penalize backtracking
       scenic_route_bonus * 0.15 +          # Reward scenic roads
       seasonal_alignment * 0.15            # Match clusters to optimal season windows
   )
   ```
4. AI agent reviews top 3 routes and selects with reasoning

### 4. Day Swap Decisions

**Question:** "Should I suggest swapping Day X with Day Y?"

This is the most complex decision in the system. See [../02-product/ITINERARY-ADAPTATION.md](../02-product/ITINERARY-ADAPTATION.md) for the full specification.

**Summary:**
```
swap_value = condition_improvement - displaced_activity_impact - logistics_friction - user_disruption
if swap_value > threshold:
    recommend_swap()
```

### 5. Packing Decisions

**Question:** "What should the user pack for this activity today?"

**Inputs:**
- Activity type and requirements
- Forecasted conditions (temperature, precipitation, wind, UV)
- Activity duration
- User fitness level (affects exertion and therefore layering)
- Terrain type

**Logic:**
```
packing_list = base_items(activity.type)  # Hiking: boots, water, snacks

# Temperature-based additions
if feels_like_temp < 5:
    add("thermal base layer", "insulated jacket", "warm gloves", "beanie")
elif feels_like_temp < 12:
    add("warm fleece/mid-layer", "light gloves")
elif feels_like_temp < 18:
    add("light layer for wind")

# Precipitation
if rain_probability > 40:
    add("waterproof jacket")
if rain_probability > 70:
    add("waterproof pants", "dry bag for electronics")

# Sun
if uv_index > 5:
    add("SPF50 sunscreen", "hat", "sunglasses")

# Wind
if wind_speed > 30:
    add("windproof layer")

# Activity-specific
if activity.involves_water:
    add("quick-dry clothes", "towel", "dry bag")
if activity.duration > 4_hours:
    add("lunch/substantial snacks", "extra water")

# Remove duplicates, order by importance
return deduplicate_and_sort(packing_list)
```

### 6. Timing Decisions

**Question:** "When should the user depart and arrive for this activity?"

**Inputs:**
- Activity scheduled time or flexible window
- Travel time from current location
- Crowd patterns (when do tour buses arrive?)
- Light conditions (golden hour for photography)
- Tide timing (for coastal activities)
- Temperature progression through the day
- Wildlife activity patterns

**Logic:**
```
base_arrival_time = activity.scheduled_time or activity.default_start_time

adjustments = []

# Crowd avoidance
if activity.popularity == "high":
    adjustments.append(("arrive 30-60 min before peak", -45))

# Photography
if user.interests.includes("photography"):
    golden_hour = calculate_golden_hour(activity.location, date)
    if activity.is_scenic and golden_hour overlaps activity window:
        adjustments.append(("arrive for golden hour", golden_hour.start))

# Tide
if activity.tide_dependent:
    ideal_tide = get_ideal_tide(activity, date)
    adjustments.append(("arrive at optimal tide", ideal_tide.time - 30min))

# Temperature
if activity.outdoors and max_temp > 28:
    adjustments.append(("start early to avoid midday heat", -120))

optimal_arrival = resolve_adjustments(base_arrival_time, adjustments)
departure_time = optimal_arrival - travel_time - buffer(15min)

return {
    "depart": departure_time,
    "arrive": optimal_arrival,
    "reasoning": explain_adjustments(adjustments)
}
```

## Decision Confidence

Every decision includes a confidence level:

```
ConfidenceLevel:
  HIGH: Based on reliable data (current conditions, tide tables, confirmed schedules)
  MEDIUM: Based on forecasts (weather 1-3 days out, crowd estimates)
  LOW: Based on patterns and heuristics (weather 4+ days out, wildlife behavior)
```

Confidence is communicated to the user naturally:
- HIGH: "Head out at 8:30 AM" (stated as fact)
- MEDIUM: "The forecast looks great for Saturday" (forecast qualifier)
- LOW: "If the weather holds, Thursday could be a good window" (conditional)

## Decision Logging

All significant decisions are logged for:
1. **Debugging**: Why did Buddi recommend X over Y?
2. **Learning**: Which recommendations were accepted? Which worked out well?
3. **Transparency**: If the user asks "why did you suggest this?", we can explain

```
DecisionLog {
  timestamp: DateTime
  decision_type: string
  inputs: object
  scoring: object
  result: object
  confidence: string
  user_response: "accepted" | "rejected" | "modified" | "pending"
  outcome: object  // Filled in post-trip if available
}
```
