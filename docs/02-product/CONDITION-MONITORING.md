# Condition Monitoring System

## Overview

The condition monitoring system is the environmental intelligence backbone of Journey Buddi. It continuously tracks weather, tides, solar activity, and other environmental factors relevant to the traveler's upcoming activities, providing the data needed for daily briefings and adaptive itinerary management.

## What We Monitor

### Weather Conditions

| Parameter | Why It Matters | Update Frequency |
|-----------|---------------|-----------------|
| Temperature (actual + feels-like) | Packing, comfort, activity feasibility | Hourly |
| Precipitation (type, probability, intensity) | Activity feasibility, safety, experience quality | Hourly |
| Wind speed + direction + gusts | Water activities, alpine hiking, comfort | Hourly |
| Cloud cover (%) | Scenic viewpoints, photography, stargazing | Hourly |
| Visibility (km) | Mountain views, driving, scenic spots | Every 3 hours |
| Humidity | Comfort, hiking exertion | Every 3 hours |
| UV Index | Sun protection needs | Daily |
| Barometric pressure trend | Weather change prediction | Hourly |

### Tide Conditions

| Parameter | Why It Matters | Update Frequency |
|-----------|---------------|-----------------|
| High tide time + height | Coastal walks, marine activities, beach access | Daily |
| Low tide time + height | Rock pools, coastal caves, Cathedral Cove access | Daily |
| Tidal range | Beach usability, kayaking, snorkeling | Daily |
| Storm surge warnings | Safety for coastal activities | As issued |

### Solar & Celestial Conditions

| Parameter | Why It Matters | Update Frequency |
|-----------|---------------|-----------------|
| Sunrise / Sunset times | Photography, activity planning, departure timing | Daily |
| Golden hour windows | Photography-focused travelers | Daily |
| Moon phase + rise/set | Stargazing, nocturnal wildlife, tide influence | Daily |
| Aurora forecast (Kp index) | Southern Lights viewing in NZ/high latitudes | Every 3 hours |
| Solar activity / geomagnetic storms | Aurora probability enhancement | Every 3 hours |
| Dark sky quality | Stargazing location quality | Daily |

### Marine & Water Conditions

| Parameter | Why It Matters | Update Frequency |
|-----------|---------------|-----------------|
| Wave height + swell period | Surfing, boat trips, coastal safety | Every 3 hours |
| Sea surface temperature | Swimming, diving comfort | Daily |
| Swell direction | Surf spot selection, boat trip comfort | Every 3 hours |
| Rip current risk | Beach safety | Daily |

### Environmental & Safety

| Parameter | Why It Matters | Update Frequency |
|-----------|---------------|-----------------|
| Road conditions / closures | Driving safety, route feasibility | As updated |
| Trail status / closures | Hiking feasibility | As updated |
| Volcanic alert levels | Safety near active volcanoes (NZ specific) | As updated |
| Avalanche risk | Winter alpine activities | Daily (seasonal) |
| Fire danger rating | Bushfire risk areas | Daily (seasonal) |

## Forecast Accuracy & Confidence

Not all environmental data can be predicted with equal accuracy at equal range. The monitoring system tracks forecast confidence alongside the data itself.

### Accuracy by Condition Type

| Condition Type | High Confidence | Medium Confidence | Low Confidence | Notes |
|---------------|----------------|-------------------|----------------|-------|
| Temperature | 0-5 days | 5-7 days | 7-10 days | Most predictable atmospheric variable |
| Precipitation | 0-3 days | 3-5 days | 5-7 days | Type (rain vs snow) more certain than intensity |
| Wind | 0-2 days | 2-4 days | 4-5 days | Gusts less predictable than sustained; terrain effects add uncertainty |
| Cloud cover | 0-2 days | 2-4 days | 4-6 days | Local effects (marine layer, valley fog) hard to predict |
| Aurora (Kp-index) | 0-1 day | 1-2 days | 2-3 days | Dependent on solar wind; requires Bt/Bz/density from ACE/DSCOVR |
| Tides | 0-90 days | N/A | N/A | Astronomical, near-perfect prediction |
| Wave/swell | 0-2 days | 2-4 days | 4-5 days | Open-ocean swell well-modeled; nearshore effects less certain |
| UV Index | 0-3 days | 3-5 days | N/A | Follows cloud cover patterns |

### Confidence Indicators in Condition Reports

Every condition score displayed to the user must include a confidence level:

```
condition_report: {
  score: 85,                    // Numeric score
  assessment: "EXCELLENT",      // Human-readable
  confidence: "high",           // high | medium | low
  confidence_reason: "Forecast is 2 days out with high model agreement"
  last_updated: "2h ago",
  next_update: "in 1h"
}
```

### Smart Look-Ahead Strategy

The monitoring system adapts its behavior based on how far out it's looking:

- **Today + tomorrow (0-1 days)**: Full condition monitoring at maximum frequency. All parameters active. Scores presented with high confidence.
- **2-3 days out**: Core parameters monitored (temperature, precipitation, wind). Scores presented with medium-high confidence. Suitable for making swap decisions.
- **4-5 days out**: Trend monitoring only. Broad patterns noted ("a weather system is approaching") but specific hour-by-hour scores not generated. Flag potential issues.
- **6+ days out**: General awareness only. "Next week looks mixed — I'll have better data in a few days." No actionable scores, no swap suggestions.

For conditions with very short accuracy windows (aurora, volcanic), monitoring intensifies as the relevant day approaches.

## Monitoring Architecture

### Data Collection Pipeline

```
External APIs → Data Fetcher → Normalization Layer → Condition Store → Analysis Engine
                                                                            ↓
                                                                    Activity Matcher
                                                                            ↓
                                                                    Alert Generator
                                                                            ↓
                                                                   User Notification
```

### Collection Strategy

**Proactive Collection:**
- For each active trip, identify all locations relevant to the next 5 days
- Fetch weather data for those locations on a scheduled basis
- Fetch tide and solar data daily (these change less frequently)

**On-Demand Collection:**
- When the user opens the app or requests a briefing
- When a swap is being evaluated and comparison data is needed
- When conditions for a new location need assessment

### Data Freshness Requirements

| Data Type | Max Staleness | Rationale |
|-----------|--------------|-----------|
| Current weather | 30 minutes | Users expect current conditions to be recent |
| Today's forecast | 1 hour | Hourly forecast updates are sufficient |
| Multi-day forecast | 6 hours | Multi-day forecasts don't change that rapidly |
| Tide data | 24 hours | Tide times are highly predictable |
| Solar/aurora | 3 hours | Aurora conditions can change quickly |
| Road/trail status | 1 hour | Safety-critical, should be current |

## Forecast Integration Sources

### Primary APIs (Structured Data)

| Provider | Data Type | Coverage | Reliability | Cost |
|----------|----------|----------|-------------|------|
| OpenWeatherMap | General weather | Global | Good | Free tier + paid |
| MetService NZ | NZ weather, warnings | New Zealand | Excellent for NZ | Free API |
| ECMWF | Premium forecast models | Global | Highest accuracy | Paid |
| Windy.com API | Wind, marine, visual | Global | Good for wind/marine | Paid |
| NOAA SWPC | Solar/aurora data | Global | Authoritative | Free |
| LINZ / NIWA | NZ tides, marine | New Zealand | Authoritative | Free |
| DOC API | Trail/road status | New Zealand | Authoritative | Free |

### Fallback: Agent Web Search

When API data is unavailable, stale, or insufficient for niche conditions:
- Agent searches the web for current condition reports
- Sources: Windy.com (visual forecasts), mountain weather services, local tourism boards
- Useful for: glacial conditions, specific river levels, volcanic activity updates, local road conditions
- The agent evaluates source reliability and recency before using web-searched data

### Data Quality Rules

- Always prefer structured API data over web-searched data
- Never present web-searched data without noting reduced confidence
- Cross-reference multiple sources when making high-impact decisions (swap recommendations)
- Cache forecast data with appropriate TTLs per condition type

### Caching Strategy

```
Cache Layer:
  L1 (Memory): Current conditions, actively viewed trips (TTL: varies by type)
  L2 (Redis): All active trip condition data (TTL: based on freshness requirements)
  L3 (Database): Historical conditions for analysis and trend detection
```

## Condition Scoring

Each activity has a condition profile defining what matters and how to score it:

```
ConditionProfile {
  activity_type: string
  critical_conditions: [
    {
      parameter: "wind_speed"
      ideal_range: [0, 20]       // km/h
      acceptable_range: [0, 40]
      deal_breaker: 60            // Above this = UNSAFE
      weight: 0.3                 // How much this matters relative to others
    },
    {
      parameter: "precipitation_probability"
      ideal_range: [0, 10]       // percentage
      acceptable_range: [0, 40]
      deal_breaker: null          // Rain isn't unsafe, just unpleasant
      weight: 0.2
    },
    {
      parameter: "cloud_cover"
      ideal_range: [0, 20]       // percentage
      acceptable_range: [0, 60]
      deal_breaker: null
      weight: 0.3
    },
    {
      parameter: "visibility"
      ideal_range: [20, 100]     // km
      acceptable_range: [5, 100]
      deal_breaker: 1             // Below 1km visibility = UNSAFE for alpine
      weight: 0.2
    }
  ]
  special_rules: [
    "If DOC issues trail closure → UNSAFE regardless of other conditions",
    "If temperature + wind chill < -5°C → escalate to POOR minimum"
  ]
}
```

### Scoring Algorithm

1. For each critical condition, calculate a normalized score (0-100):
   - Within ideal range → 80-100
   - Within acceptable range → 40-79
   - Outside acceptable range → 0-39
   - Beyond deal-breaker → -1 (forces UNSAFE)

2. Weighted average of all condition scores → Overall Score

3. Map to assessment:
   - 80-100 → 🟢 EXCELLENT
   - 60-79 → 🟡 GOOD
   - 40-59 → 🟠 FAIR
   - 20-39 → 🔴 POOR
   - < 20 or any deal-breaker → ⛔ UNSAFE

4. Apply special rules as overrides

5. Apply confidence adjustment:
   - High confidence → score as-is
   - Medium confidence → widen acceptable ranges by 20% (be more lenient)
   - Low confidence → suppress extreme scores (cap at FAIR minimum, floor at GOOD maximum) — don't trigger strong reactions on uncertain data

## Alert Triggers

The system generates alerts when:

### Immediate Alerts
- Any activity moves from GOOD/EXCELLENT to POOR/UNSAFE
- Severe weather warning issued for the user's area
- Road or trail closure affecting today's plan
- Safety hazard detected (volcanic alert, flood warning, etc.)

### Non-Urgent Updates
- Conditions improved significantly for an upcoming activity (opportunity)
- Multi-day forecast shift that affects swap planning
- Aurora forecast shows high activity (for interested users)

### Alert Suppression
- Don't alert for activities more than 3 days away (forecasts change)
- Don't alert if the change doesn't cross a threshold boundary
- Don't alert during user's quiet hours
- Don't alert for the same condition more than twice (user has been informed)

## Historical Analysis

Over time, the system builds a historical dataset that enables:

1. **Trend detection**: "Weather has been deteriorating this week — more swap suggestions likely"
2. **Forecast accuracy tracking**: How accurate were the forecasts that drove our suggestions?
3. **Destination knowledge**: Statistical patterns that improve future trip planning
4. **Seasonal intelligence**: Better pre-trip planning based on historical condition data
