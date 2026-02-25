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
  travel_group: "solo" | "couple" | "family" | "friends"
  max_driving_hours_per_day: number
  priority_locations: Location[]    // Must-visit, locked constraints
  must_not_do: string[]             // Activities/places to exclude
  flight_details: { arrival: FlightInfo, departure: FlightInfo }
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

### Stage 2.5: Provider Selection & Diversification

For each selected activity type, identify the best providers across the ENTIRE destination (not just the nearest location).

**Diversification Principle:**
Travelers want highlights spread across their journey, not clustered in one area. If a user wants skydiving, bungy, AND paragliding, the engine should distribute these across different locations rather than doing all three in Queenstown.

**Provider Evaluation Criteria:**
For each provider, evaluate and present:
1. **Experience quality** — What makes this provider's offering unique? (Views, encounter rates, duration, equipment)
2. **Reviews & ratings** — TripAdvisor and GetYourGuide scores with review count
3. **Price** — Current pricing in local currency
4. **Route fit** — How well does this provider's location fit the planned route?
5. **Diversification score** — Does choosing this provider help spread experiences geographically?

**Data Sources:**
- TripAdvisor API for reviews and ratings
- GetYourGuide API for activity details and pricing
- Destination tourism board databases
- Agent web search for new/updated providers
- Future: Journey Buddi's own provider database with direct booking

**Provider Selection Logic:**
1. For each activity type, fetch all providers across NZ
2. Score each provider on quality × route_fit × diversification
3. Present top 2-3 options to the user with clear differentiators
4. If user says "you decide," pick the option that maximizes overall trip diversity and quality

**Example:**
A user selecting "dolphin swimming" doesn't just see Kaikoura options — they see:
- Kaikoura (dusky dolphins, 95% encounter, $185, fits South Island east coast route)
- Akaroa (Hector's dolphins — world's rarest!, $165, scenic harbor, near Christchurch)
- Bay of Islands (bottlenose dolphins, $120, warmer water, North Island option)

Each with reviews, unique selling point, and route impact.

### Stage 3: Day-by-Day Allocation

Distribute activities across days within each cluster.

**Rules by pace:**

| Pace | Activities/Day | Drive Hours/Day | Rest Days |
|------|---------------|-----------------|-----------|
| Relaxed | 1-2 | ≤ 1.5h | Every 3rd day |
| Balanced | 2-3 | ≤ 2.5h | Every 4th day |
| Intensive | 3-4 | ≤ 3h | Every 5th day |

The user's `max_driving_hours_per_day` preference is a **hard constraint** — the engine must never schedule a day that exceeds this limit. If the pace table suggests a higher drive limit than the user's preference, the user's preference wins. Days that would exceed the limit must be split across two days with an overnight stop.

**Travel group impact on day structure:**
- **Solo**: Maximum flexibility — can start early, skip meals, push longer days
- **Couple**: Standard scheduling with shared decision points
- **Family**: Needs 20-30% more buffer time between activities, more frequent rest stops, earlier evening wind-down, meal breaks are non-negotiable
- **Friends**: Can handle fuller days but needs social time — don't pack every evening with activities

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

### Stage 5.5: Day Tightness Scoring

Each day receives a tightness score indicating how packed the schedule is relative to the user's pace preference and practical feasibility.

**Scoring:**
- Activities total duration + transport time + meal breaks + buffer = Day Fill Percentage

| Fill % | Score | Label | Visual |
|--------|-------|-------|--------|
| < 50% | 🟢 | Relaxed | "Plenty of breathing room" |
| 50-70% | 🟡 | Comfortable | "Good balance of activity and rest" |
| 70-85% | 🟠 | Tight | "Full day — doable but no room for delays" |
| > 85% | 🔴 | Overpacked | "This day is too tight — consider removing or moving an activity" |

**Auto-flagging:**
- Days scoring 🔴 are flagged to the user during review with a suggestion to lighten the load
- Days scoring 🟠 get a subtle warning: "This is a full day — make sure you're up for it!"
- The engine should attempt to avoid generating 🔴 days in the first place
- Two consecutive 🟠 days should trigger a suggestion to insert a rest day or lighten one of them

**Factors:**
- Activity durations (including setup and transition time)
- Transport time between activities
- Meal breaks (minimum: 30min breakfast, 45min lunch, 1h dinner)
- Buffer time (15-30min between activities for transitions)
- Travel group: families with kids need 20-30% more buffer time
- Fitness level: lower fitness = more rest time needed between strenuous activities

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

The itinerary is the single most important data structure in the entire system. It contains EVERYTHING a traveler needs to know about their trip.

```
Itinerary {
  id: string
  user_id: string
  destination: string
  status: "draft" | "confirmed" | "active" | "completed"
  dates: { start: Date, end: Date }
  total_days: number
  transport_plan: TransportPlan
  travel_group: string
  
  flights: {
    arrival: { airline, flight_number, arrives_at, airport, terminal }
    departure: { airline, flight_number, departs_at, airport, terminal }
  }
  
  trip_wide_tips: [
    {
      category: "discount" | "app" | "logistics" | "culture" | "safety"
      tip: string
      applies_to: "entire_trip" | "region" | "activity_type"
      region: string?          // If region-specific
    }
  ]

  days: [
    {
      day_number: number
      date: Date
      title: string                     // "Kaikoura — Dolphins & Whales"
      location: Location
      cluster: string
      type: "activity" | "travel" | "flex" | "arrival" | "departure"
      
      // Condition & Feasibility
      condition_forecast: {
        overall_score: "excellent" | "good" | "fair" | "poor" | "unsafe"
        confidence: "high" | "medium" | "low"   // Based on forecast distance
        key_factors: string[]                     // What's driving the score
        data_freshness: string                    // "Updated 2h ago" or "Forecast only — 5 days out"
      }
      tightness: {
        score: "relaxed" | "comfortable" | "tight" | "overpacked"
        fill_percentage: number
        suggestion: string?    // "Consider moving X to Day 8" if overpacked
      }
      
      // Activities
      activities: [
        {
          id: string
          name: string
          description: string
          duration_hours: number
          time_of_day: "morning" | "midday" | "afternoon" | "evening"
          suggested_start: Time
          suggested_end: Time
          location: Location
          google_maps_url: string
          
          // Provider details
          provider: {
            name: string
            rating: number
            review_count: number
            price: { amount: number, currency: string }
            unique_differentiator: string
            booking_url: string
            contact_phone: string?
          }
          
          // Booking status
          booking: {
            status: "not_booked" | "booked" | "confirmed" | "cancelled"
            confirmation_number: string?
            booked_time: Time?
            notes: string?
          }
          
          // Conditions
          weather_sensitivity: "low" | "moderate" | "high" | "very_high"
          conditions_needed: ConditionRequirements
          optimal_conditions_description: string
          
          // Guidance
          packing_notes: string[]
          pro_tips: string[]
          story: string?            // Legend/history/story for this place
          audio_story_available: boolean
          swap_priority: "low" | "medium" | "high"
        }
      ]
      
      // Transport
      transport: {
        mode: string
        distance_km: number
        duration_hours: number
        route_notes: string
        google_maps_route_url: string
        scenic_stops: Location[]
        fuel_stops: Location[]?     // For remote areas
      }
      
      // Accommodation
      accommodation: {
        type: "hotel" | "motel" | "airbnb" | "campervan" | "motorhome" | "hostel" | "holiday_park" | "freedom_camp"
        name: string?
        address: string?
        google_maps_url: string?
        booking_status: "not_booked" | "booked" | "confirmed"
        check_in_time: Time?
        check_out_time: Time?
        cost_per_night: { amount: number, currency: string }?
        booking_reference: string?
        notes: string?
      }
      
      // Daily essentials
      packing_list: string[]           // Consolidated for the entire day
      day_notes: string
      buddi_tips: string[]             // Per-day tips
      departure_time_suggestion: Time  // When to leave accommodation
      
      // Storytelling
      stories: [
        {
          title: string
          content: string               // The legend, history, or story
          type: "legend" | "history" | "geology" | "culture" | "fun_fact"
          audio_available: boolean
          best_consumed: "while_walking" | "evening_read" | "at_location" | "during_drive"
        }
      ]
    }
  ]
  
  // Treasure Map — Hidden gems not in the itinerary
  treasure_map: [
    {
      name: string
      description: string
      location: Location
      google_maps_url: string
      type: "viewpoint" | "beach" | "waterfall" | "cafe" | "walk" | "wildlife" | "photo_spot"
      proximity_to_route: string     // "5 min detour from Day 7 route"
      best_conditions: string
      insider_tip: string
    }
  ]
}
```

## Interactive Dashboard — Not a Chat Message

The generated itinerary is NOT delivered as a chat message or a static text dump. It is rendered as a fully interactive dashboard — a control panel for the user's trip.

**Core Principles:**
- Every element is tappable, editable, and actionable
- Booking status is visible at a glance — what's confirmed, what still needs booking
- The day view feels like scrolling through a well-designed travel app (think GetYourGuide trip pages)
- Each day card shows: condition forecast, tightness score, activities with status, transport, accommodation
- Users can drag to reorder, tap to edit, swipe to remove, and use "+" to add new activities
- Changes trigger instant re-optimization by Buddi (route, timing, feasibility validation)

**What the user sees when they open any day:**
- Condition banner at the top (how good is this day for the planned activities)
- Timeline of the day with all activities, transport, and meals
- Each activity shows: time, provider, booking status, Google Maps link, condition score
- Accommodation details with check-in/check-out
- Packing list for the day
- Stories/legends relevant to today's locations
- A "How tight is this day?" indicator

**Booking Integration (Future):**
In later phases, users can book activities directly from the dashboard. For MVP, the dashboard shows booking URLs and phone numbers, and the user updates the booking status manually (or Buddi detects bookings from email confirmations).

## Regeneration & Updates

The itinerary engine supports partial regeneration:

- **Add activity**: Insert into nearest cluster, adjust day allocation
- **Remove activity**: Rebalance affected cluster days
- **Reorder days**: Validate geographic feasibility, recalculate transport
- **Change dates**: Shift the entire itinerary, re-evaluate seasonal constraints
- **Change pace**: Re-allocate activities across days, adjust day count
- **Change accommodation type**: User switches from hotel to campervan mid-trip — recalculate accommodation zones, add freedom camping spots, adjust departure times
- **User removes an activity**: Rebalance the day, suggest alternatives or additional free time, update tightness score
- **User adds a must-do**: Find the optimal day and position for the new activity, validate feasibility, flag if it creates an overpacked day
- **Weather forces a change**: Generate a 2-3 day shuffle plan with step-by-step instructions (see ITINERARY-ADAPTATION.md)

Each change triggers a targeted re-optimization rather than full regeneration, preserving the user's choices and only adjusting what's necessary.

## Performance Targets

- Full itinerary generation: < 30 seconds
- Partial updates (add/remove activity): < 10 seconds
- Route recalculation: < 5 seconds
- All generation happens server-side with results streamed to the client
