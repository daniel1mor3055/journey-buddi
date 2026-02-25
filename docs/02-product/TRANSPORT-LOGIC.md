# Transport Recommendation Logic

## Overview

Transport is not just logistics — it's a major part of the travel experience. In New Zealand, choosing between a campervan and a car fundamentally changes the trip. In Iceland, a 4x4 vs. regular car determines which roads are accessible. Journey Buddi's transport recommendations are destination-aware, route-aware, and deeply reasoned.

## Transport Modes

### Private Vehicle Types

| Mode | Best For | Considerations |
|------|----------|---------------|
| **Rental Car** | Flexible touring, urban areas, short stays per location | Need separate accommodation, more nimble, cheaper fuel |
| **Campervan/Motorhome** | Remote areas, freedom camping, immersive nature experience | Higher rental cost, freedom camping saves on accommodation, slower on winding roads |
| **4x4/SUV** | Rough terrain, unpaved roads, highland access | Required for some routes (Iceland F-roads), otherwise overkill |
| **Motorcycle** | Adventure travelers, scenic routes, solo travel | Weather-dependent, limited luggage, not for everyone |

### Public/Shared Transport

| Mode | Best For | Considerations |
|------|----------|---------------|
| **Inter-city bus** | Budget travelers, single segments, no-drive preference | Limited schedules, less flexibility, can't stop for spur-of-moment attractions |
| **Domestic flights** | Covering long distances quickly, island hopping | Skips scenery between points, cost varies, luggage constraints |
| **Ferry** | Island-to-island crossings (NZ Cook Strait, etc.) | Must be booked, scenic experience itself, takes vehicles |
| **Train** | Scenic journeys (TranzAlpine in NZ, etc.) | Limited network, more of an experience than transport |

## Recommendation Engine

### Input Factors

1. **Route segments**: Each segment between clusters has different characteristics
2. **Accommodation availability**: Remote areas with few lodging options favor campervans
3. **Road conditions**: Some roads suit different vehicle types
4. **User preference**: Some people love campervans, others want a bed and shower at a hotel
5. **Travel group**: 
   - **Solo**: Any vehicle works. Smaller car recommended for nimbleness and cost. Consider hostel + car combo.
   - **Couple**: Mid-size car or 2-berth campervan. Campervans are particularly romantic for NZ's scenic overnight spots.
   - **Family with kids**: Larger vehicle essential. Station wagon or SUV for car option, family motorhome for campervan option. Factor in: car seats, extra space for gear, more frequent stops needed.
   - **Friends group**: Consider multiple vehicles for flexibility, or a large motorhome for the social experience. Groups of 4+ may need two cars.
6. **Budget**: Campervan rental + freedom camping vs. car rental + paid accommodation
7. **Seasonal factors**: Winter camping requires specialized vehicles; some roads close seasonally

### Max Driving Hours Per Day

The user specifies their maximum comfortable driving time per day during planning. This is a HARD constraint:

| Preference | Max Drive/Day | Impact |
|-----------|--------------|--------|
| "Short drives only" | 1-2 hours | More overnight stops, smaller geographic range, slower but more immersive |
| "Normal driving" | 3-4 hours | Standard touring pace, good coverage, time for activities |
| "Happy to drive more" | 5+ hours | Larger geographic range, longer transition days, may need designated "drive days" |

**How it affects planning:**
- Route segments exceeding the user's max are flagged and split with overnight stops
- Long drives (exceeding the max) get scenic stop suggestions to break them up
- Travel days are distinguished from activity days when drives exceed 3 hours
- If a user says "1-2 hours max" but the route requires a 4-hour segment (e.g., Queenstown to Milford Sound), Buddi explains the trade-off: "The drive to Milford Sound is 3.5 hours each way — there's no shortcut. But the drive itself is stunning and I'll point out incredible stops along the way. Think of it as a scenic activity, not just a drive."
- Family trips automatically get a 20% buffer on drive times (kids need more breaks)

### Decision Framework

For each route segment, score each viable transport mode on:

```
TransportScore {
  practicality: 1-10    // How well does it work logistically?
  experience: 1-10      // Does this mode enhance the travel experience?
  cost_efficiency: 1-10 // Total cost including accommodation impact
  flexibility: 1-10     // How much spontaneous stopping is possible?
  comfort: 1-10         // Comfort level for this segment
}
```

### New Zealand — Specific Logic

#### South Island

**West Coast (Christchurch → Glaciers → Wanaka):**
- **Recommendation: Campervan**
- Reasoning: Remote stretches between towns, incredible freedom camping spots (ocean, lake, forest), limited accommodation in some areas, the west coast is best experienced at your own pace with ability to stop anywhere
- Freedom camping spots: Ship Creek, Lake Paringa, Gillespies Beach, Lake Hawea
- Note: Some roads are narrow — mid-size campervan recommended over large motorhome

**East Coast (Christchurch → Kaikoura → Blenheim):**
- **Recommendation: Car or Campervan (either works)**
- Reasoning: More towns and accommodation options, good roads, moderate distances
- If user has campervan from west coast leg, keep it for continuity

**Queenstown/Te Anau/Milford:**
- **Recommendation: Car (or base from Queenstown)**
- Reasoning: Mountain roads to Milford are narrow and challenging for large vehicles, Queenstown has excellent accommodation, day trips work well from a base
- If user has campervan: Park at a holiday park and do day trips by car (some rental companies offer this flexibility)

**Inter-Island (South ↔ North):**
- **Recommendation: Interislander Ferry**
- Reasoning: Takes your vehicle, scenic Cook Strait crossing is an experience itself, arrives in Picton/Wellington which are great starting points
- Book in advance (especially peak season December-February)
- Consider: Bluebridge is the alternative operator, slightly cheaper

#### North Island

**Auckland → Coromandel → Rotorua → Tongariro:**
- **Recommendation: Car**
- Reasoning: Good roads, plenty of accommodation, shorter distances, more urban stops
- If user is adventurous and wants to continue the campervan experience, it works here too but adds less value than the South Island

**Specific transport experiences to suggest:**
- TranzAlpine train (Christchurch → Greymouth) — one of the world's great train journeys
- Milford Sound cruise — the activity IS the transport
- Interislander ferry — scenic strait crossing with chance of dolphins

## Multi-Modal Trip Planning

For longer trips, Buddi may recommend switching transport modes:

```
Example: 21-day Both Islands Trip

Days 1-3: Rental Car (Auckland, Coromandel, Hobbiton)
Day 4: Return car Auckland, fly to Christchurch
Days 5-15: Campervan (South Island loop)
Day 16: Return campervan Picton, ferry to Wellington
Days 17-19: Rental Car (Wellington, Tongariro, Rotorua)  
Day 20-21: Rental Car → Auckland, depart
```

### Multi-Modal Logistics

When recommending mode switches, Buddi must address:
- Where to pick up and drop off vehicles
- Booking links or references for each mode
- Luggage transfer logistics
- Timing coordination (ferry departures, flight connections)
- Cost implications of multiple rentals vs. single vehicle

## Cost Estimation

Provide rough cost comparisons to support transport decisions:

```
Example: 14-day South Island

Option A: Rental Car + Hotels/Motels
  Car: ~$60/day × 14 = $840
  Accommodation: ~$150/night × 13 = $1,950
  Total: ~$2,790

Option B: Campervan + Mix of Freedom/Holiday Parks
  Campervan: ~$180/day × 14 = $2,520
  Holiday parks (7 nights): ~$50/night × 7 = $350
  Freedom camping (6 nights): $0
  Total: ~$2,870

Option C: Campervan + Mostly Freedom Camping  
  Campervan: ~$180/day × 14 = $2,520
  Holiday parks (3 nights): ~$50/night × 3 = $150
  Freedom camping (10 nights): $0
  Total: ~$2,670
```

Costs are indicative and vary by season, vehicle size, and booking timing. Buddi should caveat estimates appropriately.

## Presentation to User

Transport recommendations are presented with:

1. **The recommendation** (what Buddi suggests)
2. **The reasoning** (why this mode for this segment)
3. **The alternative** (what else could work and the trade-offs)
4. **The logistics** (pickup/dropoff, booking needs, practical tips)
5. **The cost context** (rough comparison)

Buddi should be opinionated ("I strongly recommend a campervan for the west coast — here's why") but respect user override ("Totally fine! We'll plan car-based accommodation along the west coast instead. Here are some great options...").
