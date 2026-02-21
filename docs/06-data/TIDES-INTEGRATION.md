# Tides Integration

## Overview

Tide data is essential for Journey Buddi's coastal activity scheduling in New Zealand. Many of the most iconic NZ experiences — Cathedral Cove access, coastal walks, rock pool exploration, kayaking, and marine wildlife viewing — are directly controlled by tidal conditions. Unlike weather, tide predictions are highly deterministic (driven by celestial mechanics), making them reliable for planning days or even weeks ahead.

## Primary Provider: WorldTides API

### Why WorldTides

- Global coverage with accurate harmonic tide predictions
- Simple REST API with straightforward pricing
- Returns high/low tide events plus continuous tide height curves
- Supports datum selection (LAT, MSL, etc.)
- 7-day forecast in a single API call

### Endpoints

#### Tide Extremes (High/Low)

```
GET https://www.worldtides.info/api/v3
  ?extremes
  &lat={lat}
  &lon={lon}
  &days=7
  &datum=LAT
  &key={API_KEY}
```

Returns a list of high and low tide events with timestamps and heights.

**Response structure:**
```json
{
  "status": 200,
  "station": "Auckland",
  "lat": -36.8485,
  "lon": 174.7633,
  "datum": "LAT",
  "extremes": [
    { "dt": 1708905600, "date": "2025-02-26T00:00+0000", "height": 3.21, "type": "High" },
    { "dt": 1708928400, "date": "2025-02-26T06:20+0000", "height": 0.45, "type": "Low" },
    { "dt": 1708951200, "date": "2025-02-26T12:40+0000", "height": 3.05, "type": "High" },
    { "dt": 1708974000, "date": "2025-02-26T18:55+0000", "height": 0.62, "type": "Low" }
  ]
}
```

#### Tide Heights (Continuous Curve)

```
GET https://www.worldtides.info/api/v3
  ?heights
  &lat={lat}
  &lon={lon}
  &days=1
  &step=900          # 15-minute intervals
  &datum=LAT
  &key={API_KEY}
```

Returns tide heights at fixed intervals — useful for rendering tide charts in the UI.

#### Station Discovery

```
GET https://www.worldtides.info/api/v3
  ?stations
  &lat={lat}
  &lon={lon}
  &stationDistance=50    # km radius
  &key={API_KEY}
```

### Pricing

| Tier | Credits/Day | Monthly Cost | Notes |
|------|-------------|-------------|-------|
| Free | 50/day | $0 | Sufficient for MVP with caching |
| Basic | 500/day | $5/mo | Early growth |
| Standard | 5,000/day | $25/mo | Scale |
| Professional | 50,000/day | $100/mo | Multi-destination worldwide |

**Credit cost per request type:**

| Request | Credits |
|---------|---------|
| Extremes (7 days) | 1 |
| Heights (1 day, 15min steps) | 1 |
| Station lookup | 1 |

At 50 credits/day, the MVP can query ~50 location-days of tides daily. With caching, this is more than sufficient for dozens of active coastal trips.

## Secondary Provider: NIWA (NZ-Specific)

### Overview

NIWA (National Institute of Water and Atmospheric Research) provides New Zealand-specific tide predictions with higher accuracy for NZ stations than global providers.

### Access

NIWA publishes tide tables on their website. For programmatic access:
- NIWA Tide Forecaster: `https://tides.niwa.co.nz/`
- Structured data can be obtained via their API or by scraping published tide tables.
- The data uses NZ standard port predictions which are the most accurate available for NZ.

### NZ Standard Ports

NIWA provides primary predictions for standard ports and secondary corrections for intermediate locations:

| Standard Port | Region | Key Activities Nearby |
|---------------|--------|----------------------|
| Auckland | North Island - East | Rangitoto kayaking, Waiheke beaches |
| Tauranga | Bay of Plenty | Mount Maunganui, coastal walks |
| Whitianga | Coromandel | Cathedral Cove, Hot Water Beach |
| Gisborne | East Cape | Coastal walks, surf |
| Napier | Hawke's Bay | Cape Kidnappers gannet colony |
| Wellington | Lower North Island | South coast rock pools |
| Nelson | Top of South | Abel Tasman kayaking |
| Lyttelton | Canterbury | Banks Peninsula walks |
| Timaru | South Canterbury | Coastal access |
| Dunedin | Otago | Otago Peninsula wildlife |
| Bluff | Southland | Stewart Island access |
| Milford Sound | Fiordland | Fiord kayaking |

### Integration Approach

For NZ trips, use NIWA data as the primary source (highest accuracy) and WorldTides as a fallback. For non-NZ destinations, WorldTides is the sole provider.

```python
class TideService:
    async def get_tides(self, lat: float, lon: float, days: int = 7) -> TideCondition:
        if self._is_nz_location(lat, lon):
            try:
                return await self.niwa_adapter.fetch_tides(lat, lon, days)
            except Exception:
                pass  # fall through to WorldTides
        return await self.worldtides_adapter.fetch_tides(lat, lon, days)

    def _is_nz_location(self, lat: float, lon: float) -> bool:
        return -47.5 <= lat <= -34.0 and 166.0 <= lon <= 179.0
```

## Data We Extract

### Tide Events

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | datetime | UTC time of the tide event |
| `type` | `"high"` \| `"low"` | Type of tide extreme |
| `height_m` | float | Height above datum in meters |
| `station_id` | string | Nearest tide station identifier |
| `station_name` | string | Human-readable station name |

### Derived Data

| Derived Field | Calculation | Why It Matters |
|---------------|-------------|----------------|
| `tidal_range_m` | `high_height - low_height` | Determines beach exposure, current strength |
| `time_to_next_high` | `next_high.timestamp - now` | Real-time display in app |
| `time_to_next_low` | `next_low.timestamp - now` | Real-time display in app |
| `tide_direction` | `"incoming"` \| `"outgoing"` | Safety for coastal walks |
| `is_spring_tide` | Range > 120% of mean range | Stronger currents, wider beach exposure |
| `is_neap_tide` | Range < 80% of mean range | Gentler conditions, less beach exposure |

```python
class TideAnalyzer:
    def analyze(self, events: list[TideEvent]) -> dict:
        pairs = self._pair_highs_and_lows(events)
        ranges = [p["high"].height_m - p["low"].height_m for p in pairs]
        mean_range = sum(ranges) / len(ranges) if ranges else 0

        return {
            "events": events,
            "tidal_ranges": ranges,
            "mean_range": mean_range,
            "max_range": max(ranges) if ranges else 0,
            "is_spring_tide": max(ranges, default=0) > mean_range * 1.2,
            "is_neap_tide": max(ranges, default=0) < mean_range * 0.8,
        }

    def current_tide_state(self, events: list[TideEvent], now: datetime) -> dict:
        past = [e for e in events if e.timestamp <= now]
        future = [e for e in events if e.timestamp > now]

        last_event = past[-1] if past else None
        next_event = future[0] if future else None

        if last_event and next_event:
            direction = "incoming" if next_event.type == "high" else "outgoing"
            total_seconds = (next_event.timestamp - last_event.timestamp).total_seconds()
            elapsed = (now - last_event.timestamp).total_seconds()
            progress = elapsed / total_seconds if total_seconds > 0 else 0
        else:
            direction = "unknown"
            progress = 0

        return {
            "direction": direction,
            "progress": round(progress, 2),
            "last_event": last_event,
            "next_event": next_event,
            "minutes_to_next": int((next_event.timestamp - now).total_seconds() / 60) if next_event else None,
        }
```

## Tide-Dependent Activities

### Activity Tide Requirements

| Activity | Tide Requirement | Access Window | Safety Concern |
|----------|-----------------|---------------|----------------|
| Cathedral Cove walk-through | Low tide only | ±2h around low tide | Cut off at mid-high tide |
| Hot Water Beach digging | Low tide ±2h | 2h before to 1h after low | Thermal burns if not dug properly |
| Abel Tasman coastal track | Low tide for beach sections | Check specific sections | Some beaches impassable at high |
| Rock pool exploring | Low tide best | ±1.5h around low | Slippery, wave danger at incoming |
| Coastal kayaking | Slack tide preferred | ±1h around high or low slack | Strong tidal currents mid-tide |
| Moeraki Boulders | Low–mid tide | Best at low tide for access | Waves at high tide |
| Wharariki Beach caves | Low tide | ±2h around low | Cut off at high tide |
| Bay of Islands kayaking | Aware of currents | Any, but plan with tide | Tidal flow through passages |
| Raglan surf | Depends on break | Mid-rising tide often best | Rips stronger at outgoing |
| Kaikōura rock pools | Low tide | ±2h around low | Seal territory, wave danger |

### Tide-Activity Scheduling Logic

```python
class TideActivityScheduler:
    TIDE_REQUIREMENTS = {
        "cathedral_cove_walk": {
            "required_tide": "low",
            "window_hours_before": 2.0,
            "window_hours_after": 2.0,
            "deal_breaker": True,
        },
        "hot_water_beach": {
            "required_tide": "low",
            "window_hours_before": 2.0,
            "window_hours_after": 1.0,
            "deal_breaker": True,
        },
        "rock_pool_exploring": {
            "required_tide": "low",
            "window_hours_before": 1.5,
            "window_hours_after": 1.5,
            "deal_breaker": False,  # still possible at other times, just worse
        },
        "coastal_kayaking": {
            "required_tide": "slack",
            "window_hours_before": 1.0,
            "window_hours_after": 1.0,
            "deal_breaker": False,
        },
    }

    def find_best_time(
        self, activity_type: str, tide_events: list[TideEvent], date: datetime
    ) -> dict | None:
        req = self.TIDE_REQUIREMENTS.get(activity_type)
        if not req:
            return None

        target_events = [
            e for e in tide_events
            if e.type == req["required_tide"] and e.timestamp.date() == date.date()
        ]

        windows = []
        for event in target_events:
            window_start = event.timestamp - timedelta(hours=req["window_hours_before"])
            window_end = event.timestamp + timedelta(hours=req["window_hours_after"])
            windows.append({
                "optimal_time": event.timestamp,
                "window_start": window_start,
                "window_end": window_end,
                "tide_height_m": event.height_m,
            })

        return windows[0] if windows else None
```

### How Tide Data Feeds the AI Agent

When generating a daily itinerary, the AI agent:

1. Queries today's and tomorrow's tide events for the trip's coastal locations.
2. For each tide-dependent activity, identifies valid access windows.
3. Pins tide-dependent activities to their windows first, then fills remaining slots around them.
4. In the daily briefing, Buddi mentions: *"Low tide at Cathedral Cove is at 10:42am — perfect window is roughly 8:45am to 12:45pm. I've scheduled you to arrive by 9:30am."*

## Caching Strategy

Tide predictions are based on harmonic analysis of gravitational forces (moon + sun). They are highly deterministic and change only due to meteorological effects (storm surge, atmospheric pressure). This means aggressive caching is safe.

### Cache TTLs

| Data Type | Redis TTL | Rationale |
|-----------|-----------|-----------|
| 7-day tide extremes | 24 hours | Predictions don't change; one refresh per day |
| Tide height curve (15min steps) | 12 hours | Useful for UI chart, doesn't change |
| Station metadata | 7 days | Stations don't move |
| Derived analysis (ranges, spring/neap) | 24 hours | Recomputed daily |

### Cache Key Structure

```
tide:{provider}:{station_id}:{data_type}:{date_range}
```

Example: `tide:worldtides:auckland:extremes:2025-02-26_to_2025-03-04`

### Prefetch Strategy

- On trip creation: Fetch full tide data for all coastal locations in the itinerary. This is a one-time cost that covers the entire trip.
- Daily refresh: Re-fetch today's and tomorrow's tide data to capture any meteorological adjustments.
- Proactive alert: If a significant storm is approaching, re-fetch tides more frequently since storm surge can modify actual water levels.

```python
@shared_task
def prefetch_tides_for_new_trip(trip_id: str):
    trip = get_trip(trip_id)
    coastal_locations = trip.get_coastal_locations()
    for loc in coastal_locations:
        station = find_nearest_tide_station(loc.lat, loc.lon)
        tides = fetch_tide_extremes(station.id, days=trip.duration_days)
        cache_tides(station.id, tides, ttl=86400)
```

## Storm Surge and Anomalies

While tide predictions are deterministic, actual water levels can differ due to:

| Factor | Effect | How We Handle |
|--------|--------|---------------|
| Storm surge | Water levels 0.5–2m above predicted | Cross-reference with severe weather alerts |
| Low pressure systems | Water rises ~1cm per 1 hPa drop | Adjust predictions using barometric data from weather integration |
| Strong onshore wind | Water pushed higher on coast | Factor wind direction/speed from weather data |
| King tides | Unusually high spring tides | Detected automatically from tidal range analysis |

When storm conditions are detected (from the weather integration), the system adds a warning:

```python
def assess_storm_surge_risk(weather: WeatherCondition, tide: TideEvent) -> str | None:
    if tide.type != "high":
        return None
    surge_risk = False
    if weather.pressure_hpa < 990:
        surge_risk = True
    if weather.wind_speed_kmh > 60 and is_onshore_wind(weather.wind_direction_deg, coast_orientation):
        surge_risk = True
    if surge_risk and tide.height_m > mean_high_water:
        return (
            f"Storm surge risk: High tide at {tide.timestamp.strftime('%H:%M')} "
            f"({tide.height_m:.1f}m) combined with low pressure ({weather.pressure_hpa} hPa) "
            f"and strong winds ({weather.wind_speed_kmh:.0f} km/h). "
            f"Avoid coastal areas near high tide."
        )
    return None
```

## NZ Tide Station Reference

Key tide stations for the NZ pilot and their nearest attractions:

| Station | Lat | Lon | Key Attractions |
|---------|-----|-----|----------------|
| Whitianga | -36.833 | 175.700 | Cathedral Cove, Hot Water Beach |
| Tauranga | -37.650 | 176.167 | Mount Maunganui, Moturiki Island |
| Auckland | -36.849 | 174.763 | Rangitoto, Waiheke |
| Kaikōura | -42.400 | 173.683 | Seal colony, rock pools, whale watching |
| Abel Tasman | -40.900 | 173.000 | Coastal track, kayaking |
| Milford Sound | -44.667 | 167.917 | Kayaking, boat cruises |
| Dunedin (Port Chalmers) | -45.817 | 170.633 | Otago Peninsula wildlife |
| Raglan | -37.800 | 174.867 | Surfing |
| Moeraki | -45.350 | 170.833 | Moeraki Boulders |
| Akaroa | -43.817 | 172.967 | Banks Peninsula, dolphins |

## Data Normalization

### WorldTides → Canonical Schema

```python
class WorldTidesAdapter:
    async def fetch_tides(self, lat: float, lon: float, days: int = 7) -> TideCondition:
        params = {
            "extremes": "",
            "lat": lat,
            "lon": lon,
            "days": days,
            "datum": "LAT",
            "key": self.api_key,
        }
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        events = [
            TideEvent(
                timestamp=datetime.utcfromtimestamp(e["dt"]),
                type="high" if e["type"] == "High" else "low",
                height_m=round(e["height"], 2),
                station_id=data.get("station", "unknown"),
                station_name=data.get("station", "unknown"),
            )
            for e in data.get("extremes", [])
        ]

        return TideCondition(
            station_id=data.get("station", "unknown"),
            station_name=data.get("station", "unknown"),
            location_lat=data["requestLat"],
            location_lon=data["requestLon"],
            provider="worldtides",
            events=events,
            datum=data.get("datum", "LAT"),
        )
```

## Cross-References

- **Tide condition monitoring**: See [Condition Monitoring](../02-product/CONDITION-MONITORING.md)
- **Canonical data schemas**: See [Data Integrations Overview](./DATA-INTEGRATIONS-OVERVIEW.md)
- **Activity scheduling with tides**: See [Activity Guidance](../02-product/ACTIVITY-GUIDANCE.md)
- **Moon phase influence on tides**: See [Solar Activity Integration](./SOLAR-ACTIVITY-INTEGRATION.md)
