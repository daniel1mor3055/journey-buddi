# Itinerary Generation Engine

## Overview

The itinerary generation engine is the core algorithmic component that transforms user selections into a coherent, optimized day-by-day travel plan. It combines AI reasoning with constraint satisfaction to produce itineraries that are geographically efficient, pace-appropriate, and condition-aware.

## Input Requirements

The engine requires the following inputs (accumulated during the planning conversation):

```
ItineraryRequest {
  user_profile: UserProfile
  destination: Destination
  dates: { start: Date, end: Date, flexible: boolean }
  entry_point: Location       // Airport/city of arrival
  exit_point: Location        // Airport/city of departure
  attractions: Attraction[]   // Selected attractions with locations
  transport_preferences: TransportPlan
  pace: "relaxed" | "balanced" | "intensive"
  locked_constraints: Constraint[]  // "Must be in X on date Y"
}
```

## Generation Pipeline

### Stage 1: Geographic Clustering

Group selected attractions into geographic clusters — areas where multiple activities can be done from a single base.

**Algorithm:**
1. Plot all selected attractions on a coordinate grid
2. Apply hierarchical clustering with a maximum distance threshold (roughly 1-hour drive radius)
3. Name each cluster by its primary area (e.g., "Kaikoura Area", "Queenstown Region")
4. Calculate estimated days needed per cluster based on activity count and pace preference

**Example output:**
```
Cluster: Kaikoura Area
  - Dolphin swimming (half day)
  - Whale watching (half day)
  - Seal colony walk (2 hours)
  - Peninsula walkway (3 hours)
  Estimated days: 2-3

Cluster: Glacier Country
  - Franz Josef glacier hike (half day)
  - Lake Matheson mirror walk (2 hours)
  Estimated days: 1-2
```

### Stage 2: Route Optimization

Determine the optimal sequence to visit clusters, minimizing total travel time while respecting entry/exit points.

**Approach:**
This is a variant of the Traveling Salesman Problem with fixed start and end points. For the number of clusters typical in a 2-3 week trip (8-15 clusters), we can use:

1. Generate all feasible route permutations (with heuristic pruning)
2. Score each route on: total drive time, backtracking penalty, scenic route bonus
3. Present the top 1-2 route options to the AI agent for final selection with reasoning

**Constraints:**
- Entry point must be first cluster
- Exit point must be last cluster (or near last)
- Ferry crossings constrain North/South Island ordering
- Some roads are one-way seasonal (e.g., some NZ mountain passes)
- Some areas have limited access windows

### Stage 3: Day-by-Day Allocation

Distribute activities across days within each cluster.

**Rules by pace:**

| Pace | Activities/Day | Drive Hours/Day | Rest Days |
|------|---------------|-----------------|-----------|
| Relaxed | 1-2 | ≤ 1.5h | Every 3rd day |
| Balanced | 2-3 | ≤ 2.5h | Every 4th day |
| Intensive | 3-4 | ≤ 3h | Every 5th day |

**Activity scheduling logic:**
- **Morning activities**: Hikes (cooler, less crowded), wildlife viewing (animals more active), photography (morning light)
- **Midday activities**: Indoor/covered activities, lunch stops, short drives
- **Afternoon activities**: Water sports (wind typically drops), cultural visits, scenic drives
- **Evening activities**: Glowworms, stargazing, penguin parades, sunset viewpoints

**Constraint satisfaction:**
- No two strenuous activities on consecutive days (unless intensive pace)
- Travel days (>3h drive) get lighter activity loads
- Weather-sensitive activities should be spread across the trip (not clustered) to maximize swap flexibility
- Activities with narrow time windows (e.g., penguin parade at dusk) are placed accordingly

### Stage 4: Transport Integration

Insert transport segments between days/clusters.

**For each transition:**
- Calculate drive time and distance
- Identify interesting stops along the route (break up long drives)
- Note fuel/charging stations for remote areas
- Flag ferry bookings needed
- Suggest scenic vs. fast route options

### Stage 5: Flex Day Insertion

Add buffer days for weather-dependent flexibility.

**Logic:**
- Analyze the ratio of weather-sensitive activities to total activities
- Insert flex days after clusters with high weather sensitivity
- Position flex days to enable the most swap options
- Flex days get "discovery" suggestions (explore the area, local markets, etc.) but are primarily there for itinerary flexibility

### Stage 6: Condition Pre-Analysis

For each activity, document what conditions matter and why.

```
Activity: Tongariro Alpine Crossing
  Weather sensitivity: VERY HIGH
  Key conditions:
    - Wind: Must be < 60 km/h (DOC closes the track above this)
    - Rain: Heavy rain makes the track dangerous
    - Cloud: Low cloud ruins the volcanic landscape views
    - Temperature: Summit can be 15°C colder than base
  Optimal conditions: Clear, calm, cool morning
  Swap priority: HIGH (one of the most condition-dependent activities)
  
Activity: Milford Sound Cruise
  Weather sensitivity: MODERATE (interesting in all weather)
  Key conditions:
    - Rain: Actually creates temporary waterfalls — some prefer rain!
    - Cloud: Low cloud creates atmospheric mood but hides peaks
    - Clear: Best for photography and mountain views
  Optimal conditions: Clear morning for views, rain has its own magic
  Swap priority: LOW (rewarding in most conditions)
```

### Stage 7: AI Review & Enrichment

The complete itinerary is passed to the AI agent for final review:

1. **Logical coherence check**: Does the flow make sense? Any obvious improvements?
2. **Knowledge enrichment**: Add pro tips, timing advice, and hidden gems for each day
3. **Narrative arc**: Does the trip tell a story? Build anticipation? Have climactic moments?
4. **Practical validation**: Are accommodation zones realistic? Are timing estimates accurate?

The AI may suggest adjustments based on knowledge that the algorithmic engine doesn't have (e.g., "Day 7's drive passes through Arthur's Pass — suggest a lunch stop at the viaduct lookout").

## Output Format

```
Itinerary {
  id: string
  user_id: string
  destination: string
  status: "draft" | "confirmed" | "active" | "completed"
  dates: { start: Date, end: Date }
  total_days: number
  transport_plan: TransportPlan
  days: [
    {
      day_number: number
      date: Date
      title: string              // "Kaikoura — Dolphins & Whales"
      location: Location
      cluster: string
      type: "activity" | "travel" | "flex" | "arrival" | "departure"
      activities: [
        {
          id: string
          name: string
          description: string
          duration_hours: number
          time_of_day: "morning" | "midday" | "afternoon" | "evening"
          suggested_start: Time
          location: Location
          weather_sensitivity: "low" | "moderate" | "high" | "very_high"
          conditions_needed: ConditionRequirements
          packing_notes: string[]
          pro_tips: string[]
          swap_priority: "low" | "medium" | "high"
        }
      ]
      transport: {
        mode: string
        distance_km: number
        duration_hours: number
        route_notes: string
        scenic_stops: Location[]
      }
      accommodation_zone: string
      day_notes: string
      buddi_tips: string[]
    }
  ]
}
```

## Regeneration & Updates

The itinerary engine supports partial regeneration:

- **Add activity**: Insert into nearest cluster, adjust day allocation
- **Remove activity**: Rebalance affected cluster days
- **Reorder days**: Validate geographic feasibility, recalculate transport
- **Change dates**: Shift the entire itinerary, re-evaluate seasonal constraints
- **Change pace**: Re-allocate activities across days, adjust day count

Each change triggers a targeted re-optimization rather than full regeneration, preserving the user's choices and only adjusting what's necessary.

## Performance Targets

- Full itinerary generation: < 30 seconds
- Partial updates (add/remove activity): < 10 seconds
- Route recalculation: < 5 seconds
- All generation happens server-side with results streamed to the client
