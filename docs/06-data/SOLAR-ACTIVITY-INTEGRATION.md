# Solar Activity Integration

## Overview

Solar, celestial, and aurora data drives several key Journey Buddi features: sunrise/sunset timing for activity planning, golden hour calculations for photography enthusiasts, moon phase tracking for stargazing and nocturnal wildlife, Southern Lights forecasting for high-latitude trips, and UV index for outdoor preparation. Unlike weather, most of this data is either deterministic (sunrise/sunset, moon phase) or infrequently updated (aurora forecasts), making it inexpensive to integrate.

## Sunrise & Sunset Data

### Provider: sunrise-sunset.org

A free, no-auth-required API that returns sunrise, sunset, twilight times, and day length for any coordinate and date.

### Endpoint

```
GET https://api.sunrise-sunset.org/json
  ?lat={lat}
  &lng={lon}
  &date={YYYY-MM-DD}
  &formatted=0          # returns ISO 8601 timestamps
```

### Response Structure

```json
{
  "results": {
    "sunrise": "2025-02-26T18:30:00+00:00",
    "sunset": "2025-02-27T07:15:00+00:00",
    "solar_noon": "2025-02-26T00:52:30+00:00",
    "day_length": 45900,
    "civil_twilight_begin": "2025-02-26T18:05:00+00:00",
    "civil_twilight_end": "2025-02-27T07:40:00+00:00",
    "nautical_twilight_begin": "2025-02-26T17:35:00+00:00",
    "nautical_twilight_end": "2025-02-27T08:10:00+00:00",
    "astronomical_twilight_begin": "2025-02-26T17:02:00+00:00",
    "astronomical_twilight_end": "2025-02-27T08:43:00+00:00"
  },
  "status": "OK"
}
```

### Fields We Extract

| Field | Schema Field | Use Case |
|-------|-------------|----------|
| `sunrise` | `sunrise` | Activity start times, departure planning |
| `sunset` | `sunset` | Return-by times, evening planning |
| `solar_noon` | `solar_noon` | Harshest UV, avoid midday hikes |
| `day_length` | `day_length_hours` | Trip pacing (summer = more time) |
| `civil_twilight_begin` | `civil_dawn` | Safe hiking start time |
| `civil_twilight_end` | `civil_dusk` | Last safe return time |
| `nautical_twilight_end` | `nautical_dusk` | Stargazing viable after this |
| `astronomical_twilight_end` | `astro_dusk` | True dark sky begins |

### Pricing

Completely free, no API key required. Rate limit: ~1 request/second (unofficial, be respectful).

### Fallback: Local Calculation

If the API is unavailable, sunrise/sunset can be computed locally using the `astral` Python library:

```python
from astral import LocationInfo
from astral.sun import sun
from datetime import date

def calculate_solar_times(lat: float, lon: float, d: date, timezone: str) -> dict:
    location = LocationInfo(latitude=lat, longitude=lon, timezone=timezone)
    s = sun(location.observer, date=d, tzinfo=location.timezone)
    return {
        "sunrise": s["sunrise"],
        "sunset": s["sunset"],
        "solar_noon": s["noon"],
        "dawn": s["dawn"],       # civil dawn
        "dusk": s["dusk"],       # civil dusk
    }
```

This is a zero-dependency-on-external-API fallback that can be used indefinitely. The `astral` library produces results accurate to within ~1 minute.

## Golden Hour Calculations

### What is Golden Hour

Golden hour is the period shortly after sunrise and before sunset when sunlight is softer, warmer, and ideal for photography. Journey Buddi calculates this for photography-focused travelers.

### Calculation

Golden hour is approximately the period when the sun is between 0° and 6° above the horizon. A practical approximation:

- **Morning golden hour**: From sunrise to ~45–60 minutes after sunrise
- **Evening golden hour**: From ~45–60 minutes before sunset to sunset

The exact duration depends on latitude and season (longer at higher latitudes, shorter near the equator).

```python
from astral import LocationInfo
from astral.sun import golden_hour, blue_hour
from datetime import date

def calculate_golden_hours(lat: float, lon: float, d: date, timezone: str) -> dict:
    location = LocationInfo(latitude=lat, longitude=lon, timezone=timezone)

    try:
        morning_start, morning_end = golden_hour(
            location.observer, date=d, direction=1  # morning (SUN_RISING)
        )
        evening_start, evening_end = golden_hour(
            location.observer, date=d, direction=-1  # evening (SUN_SETTING)
        )
    except ValueError:
        return None  # polar regions or extreme latitudes

    return {
        "golden_hour_morning_start": morning_start,
        "golden_hour_morning_end": morning_end,
        "golden_hour_evening_start": evening_start,
        "golden_hour_evening_end": evening_end,
    }
```

### How Golden Hour Is Used

- **Photography enthusiasts**: Buddi suggests scenic viewpoints during golden hour windows. *"Golden hour at Roy's Peak starts at 6:42pm — if you begin the descent at 5pm, you'll hit the summit viewpoint right at golden light."*
- **Activity ordering**: When two activities have similar conditions, the more scenic one is scheduled during golden hour.
- **Sunrise/sunset experiences**: Activities tagged as `sunset_worthy` or `sunrise_worthy` are matched to these windows.

## Moon Phase Data

### Provider: Astronomy API (or OpenWeatherMap daily data)

OpenWeatherMap's daily forecast includes `moon_phase` (0–1 float), which is sufficient and avoids an additional API dependency.

| `moon_phase` Value | Phase Name | Icon |
|--------------------|-----------|------|
| 0.0 | New Moon | 🌑 |
| 0.125 | Waxing Crescent | 🌒 |
| 0.25 | First Quarter | 🌓 |
| 0.375 | Waxing Gibbous | 🌔 |
| 0.5 | Full Moon | 🌕 |
| 0.625 | Waning Gibbous | 🌖 |
| 0.75 | Last Quarter | 🌗 |
| 0.875 | Waning Crescent | 🌘 |
| 1.0 | New Moon | 🌑 |

### Alternative: Astral Library (Local Calculation)

```python
from astral import moon

def get_moon_phase(d: date) -> dict:
    phase_value = moon.phase(d)  # returns 0-27.99

    phase_normalized = phase_value / 27.99
    if phase_value < 1.8:
        name = "New Moon"
    elif phase_value < 5.4:
        name = "Waxing Crescent"
    elif phase_value < 9.0:
        name = "First Quarter"
    elif phase_value < 12.6:
        name = "Waxing Gibbous"
    elif phase_value < 16.2:
        name = "Full Moon"
    elif phase_value < 19.8:
        name = "Waning Gibbous"
    elif phase_value < 23.4:
        name = "Last Quarter"
    elif phase_value < 27.0:
        name = "Waning Crescent"
    else:
        name = "New Moon"

    return {
        "phase_value": round(phase_normalized, 3),
        "phase_name": name,
        "illumination_pct": round(abs(1 - abs(phase_normalized - 0.5) * 2) * 100, 1),
    }
```

### How Moon Phase Is Used

| Moon Phase | Impact On | AI Agent Behavior |
|------------|-----------|-------------------|
| New Moon (dark) | Stargazing: excellent | Suggest stargazing locations, aurora viewing |
| New Moon (dark) | Nocturnal wildlife: less visible | Lower expectations for kiwi spotting |
| Full Moon | Stargazing: poor | De-prioritize stargazing activities |
| Full Moon | Nocturnal wildlife: more visible | Better chance for kiwi, penguin watching |
| Full Moon | Tides: spring tides | Flag potential king tides for coastal activities |
| Waxing/Waning | Moderate | No special adjustments |

## Aurora / Southern Lights Forecasting

### Provider: NOAA Space Weather Prediction Center

NOAA's Space Weather Prediction Center provides free, public geomagnetic activity data that drives aurora predictions.

### Key Data Points

#### Planetary Kp Index

The Kp index (0–9) measures global geomagnetic disturbance. Higher Kp = more aurora activity.

```
GET https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json
```

Returns recent and forecast Kp values:

```json
[
  ["time_tag", "Kp", "a_running", "station_count"],
  ["2025-02-26 00:00:00.000", "2.67", "10.17", "8"],
  ["2025-02-26 03:00:00.000", "3.33", "12.50", "8"]
]
```

#### 3-Day Geomagnetic Forecast

```
GET https://services.swpc.noaa.gov/text/3-day-forecast.txt
```

Returns a human-readable 3-day geomagnetic forecast with predicted Kp values.

#### Aurora Oval Position (27-Day Forecast)

```
GET https://services.swpc.noaa.gov/products/animations/ovation_south_24h.json
```

Provides the predicted position and intensity of the auroral oval — the ring around the magnetic pole where aurora is visible.

### Kp Index Interpretation for Southern Lights in NZ

| Kp Index | Aurora Visibility in NZ | AI Agent Action |
|----------|------------------------|-----------------|
| 0–2 | Not visible from NZ | No mention |
| 3–4 | Possibly visible from Stewart Island / deep south | Mention to interested users in Southland |
| 5–6 | Visible from South Island south coast | Alert users in South Island |
| 7–8 | Visible across most of South Island | Proactive notification, suggest dark sky locations |
| 9 | Visible even from North Island | High-priority alert for all NZ users |

### Aurora Alert Logic

```python
from datetime import datetime

class AuroraService:
    MINIMUM_KP_NZ_SOUTH = 4  # Stewart Island, Southland
    MINIMUM_KP_NZ_SOUTH_ISLAND = 5  # Queenstown, Dunedin
    MINIMUM_KP_NZ_NORTH_ISLAND = 7  # Visible from North Island

    async def check_aurora_opportunity(self, lat: float, lon: float) -> dict | None:
        kp_data = await self._fetch_kp_index()
        current_kp = kp_data["current"]
        forecast_kp_max = kp_data["forecast_max_24h"]

        threshold = self._get_threshold_for_latitude(lat)
        if threshold is None:
            return None

        if current_kp >= threshold or forecast_kp_max >= threshold:
            cloud_cover = await self._get_cloud_cover(lat, lon)
            solar = await self._get_solar_times(lat, lon)

            if cloud_cover > 70:
                return {
                    "alert": False,
                    "reason": "Aurora possible but cloud cover too high",
                    "kp": current_kp,
                }

            best_viewing = self._calculate_viewing_window(solar)
            return {
                "alert": True,
                "kp_current": current_kp,
                "kp_forecast_max": forecast_kp_max,
                "probability": self._kp_to_probability(current_kp, lat),
                "best_viewing_start": best_viewing["start"],
                "best_viewing_end": best_viewing["end"],
                "look_direction": "south",
                "cloud_cover_pct": cloud_cover,
                "message": self._generate_message(current_kp, forecast_kp_max, cloud_cover),
            }
        return None

    def _get_threshold_for_latitude(self, lat: float) -> int | None:
        if lat <= -46:
            return self.MINIMUM_KP_NZ_SOUTH
        elif lat <= -43:
            return self.MINIMUM_KP_NZ_SOUTH_ISLAND
        elif lat <= -34:
            return self.MINIMUM_KP_NZ_NORTH_ISLAND
        return None  # too far north for Southern Lights

    def _kp_to_probability(self, kp: float, lat: float) -> str:
        threshold = self._get_threshold_for_latitude(lat)
        excess = kp - threshold
        if excess >= 3:
            return "high"
        elif excess >= 1:
            return "moderate"
        return "low"

    def _generate_message(self, kp_current: float, kp_max: float, cloud_cover: float) -> str:
        if kp_current >= 7:
            intensity = "a strong"
        elif kp_current >= 5:
            intensity = "a moderate"
        else:
            intensity = "a possible"

        cloud_note = ""
        if cloud_cover > 30:
            cloud_note = f" Cloud cover is at {cloud_cover:.0f}%, which may limit visibility."

        return (
            f"There's {intensity} Southern Lights opportunity tonight "
            f"(Kp index: {kp_current:.1f}, forecast peak: {kp_max:.1f}). "
            f"Look toward the southern horizon after astronomical twilight.{cloud_note}"
        )
```

### Viewing Window Calculation

Aurora is only visible after astronomical twilight (when the sky is truly dark):

```python
def _calculate_viewing_window(self, solar: SolarCondition) -> dict:
    return {
        "start": solar.astro_dusk,     # true dark begins
        "end": solar.astro_dawn,       # true dark ends (next morning)
        "peak": solar.midnight_solar,  # magnetic midnight (approx)
    }
```

## Dark Sky Quality Assessment

### Purpose

For stargazing activities, the system assesses dark sky quality based on:
- Moon phase and illumination
- Cloud cover
- Light pollution (from static database)
- Time relative to astronomical twilight

### Dark Sky Score

```python
def calculate_dark_sky_score(
    moon_illumination_pct: float,
    cloud_cover_pct: float,
    light_pollution_bortle: int,   # 1 (darkest) to 9 (city center)
    time_after_astro_twilight_min: int,
) -> dict:
    moon_score = max(0, 100 - moon_illumination_pct)  # 0-100
    cloud_score = max(0, 100 - cloud_cover_pct)         # 0-100
    bortle_score = max(0, (9 - light_pollution_bortle) / 8 * 100)  # 0-100
    twilight_score = min(100, time_after_astro_twilight_min / 60 * 100)  # ramp up over 60 min

    overall = (
        moon_score * 0.30 +
        cloud_score * 0.35 +
        bortle_score * 0.25 +
        twilight_score * 0.10
    )

    if overall >= 80:
        rating = "Excellent"
    elif overall >= 60:
        rating = "Good"
    elif overall >= 40:
        rating = "Fair"
    else:
        rating = "Poor"

    return {
        "score": round(overall, 1),
        "rating": rating,
        "factors": {
            "moon": f"{moon_illumination_pct:.0f}% illuminated",
            "clouds": f"{cloud_cover_pct:.0f}% cover",
            "light_pollution": f"Bortle {light_pollution_bortle}",
        },
    }
```

### NZ Dark Sky Locations

| Location | Bortle Class | Notes |
|----------|-------------|-------|
| Aoraki Mackenzie International Dark Sky Reserve | 1–2 | World-class, certified reserve |
| Great Barrier Island | 2–3 | Dark Sky Sanctuary |
| Stewart Island | 2–3 | Southernmost, aurora viewing |
| Wairarapa | 3–4 | Good access from Wellington |
| Tongariro National Park | 3 | Mountain stargazing |
| Tekapo / Lake Pukaki | 1–2 | Part of Mackenzie reserve |

## UV Index Integration

### Provider: OpenUV API

```
GET https://api.openuv.io/api/v1/uv
  ?lat={lat}
  &lng={lon}
  &dt={ISO_8601_datetime}

Headers:
  x-access-token: {API_KEY}
```

### Response

```json
{
  "result": {
    "uv": 6.2,
    "uv_max": 11.4,
    "uv_max_time": "2025-02-26T01:30:00.000Z",
    "safe_exposure_time": {
      "st1": 30,   // Skin type I (very fair)
      "st2": 37,   // Skin type II (fair)
      "st3": 50,   // Skin type III (medium)
      "st4": 67,   // Skin type IV (olive)
      "st5": 100,  // Skin type V (brown)
      "st6": 117   // Skin type VI (dark)
    },
    "sun_info": {
      "sun_times": {
        "sunrise": "2025-02-26T18:30:00.000Z",
        "sunset": "2025-02-27T07:15:00.000Z"
      }
    }
  }
}
```

### UV Alert Thresholds

| UV Index | Category | AI Agent Action |
|----------|----------|-----------------|
| 0–2 | Low | No mention |
| 3–5 | Moderate | Include in briefing: "Moderate UV today, sunscreen recommended" |
| 6–7 | High | Proactive warning: "High UV — apply SPF 50, wear a hat" |
| 8–10 | Very High | Activity timing: "Avoid outdoor exposure 11am–2pm" |
| 11+ | Extreme | Strong warning, suggest indoor alternatives for midday |

NZ has notoriously high UV due to the ozone hole and clear southern atmosphere. UV indices of 12–13 are common in summer.

### Fallback

OpenWeatherMap's daily forecast includes a `uvi` field. If OpenUV is rate-limited (50 free requests/day), fall back to the weather integration's UV data.

## Caching Strategy (All Solar Data)

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Sunrise/sunset | 7 days | Deterministic, precomputable |
| Golden hour | 7 days | Derived from sunrise/sunset |
| Moon phase | 7 days | Deterministic |
| Aurora Kp index (current) | 30 minutes | Changes with solar activity |
| Aurora forecast (3-day) | 3 hours | Updated every 3 hours by NOAA |
| UV index (today) | 2 hours | Updates through the day |
| Dark sky score | 6 hours | Composite of multiple inputs |

### Batch Precomputation

On trip creation, precompute all deterministic solar data for the trip's entire date range and all locations:

```python
@shared_task
def precompute_solar_data(trip_id: str):
    trip = get_trip(trip_id)
    for day in trip.date_range():
        for loc in trip.get_locations_for_date(day):
            solar = calculate_solar_times(loc.lat, loc.lon, day, trip.timezone)
            golden = calculate_golden_hours(loc.lat, loc.lon, day, trip.timezone)
            moon = get_moon_phase(day)

            cache_solar(loc, day, {**solar, **golden, **moon}, ttl=604800)
```

This is a one-time computation per trip. For a 14-day trip with 20 locations, that's 280 precomputed records — trivial cost.

## Canonical Schema

```python
class SolarCondition(BaseModel):
    """Solar, celestial, and aurora data for a date and location."""
    date: date
    location_lat: float
    location_lon: float

    # Sun
    sunrise: datetime
    sunset: datetime
    solar_noon: datetime
    day_length_hours: float
    civil_dawn: datetime
    civil_dusk: datetime
    nautical_dawn: Optional[datetime]
    nautical_dusk: Optional[datetime]
    astro_dawn: Optional[datetime]
    astro_dusk: Optional[datetime]

    # Golden hour
    golden_hour_morning_start: Optional[datetime]
    golden_hour_morning_end: Optional[datetime]
    golden_hour_evening_start: Optional[datetime]
    golden_hour_evening_end: Optional[datetime]

    # Moon
    moon_phase: float              # 0.0–1.0
    moon_phase_name: str
    moon_illumination_pct: float
    moonrise: Optional[datetime]
    moonset: Optional[datetime]

    # Aurora
    aurora_kp_index: Optional[float]
    aurora_probability: Optional[str]  # "none", "low", "moderate", "high"
    aurora_message: Optional[str]

    # UV
    uv_index_current: Optional[float]
    uv_index_max: Optional[float]
    uv_max_time: Optional[datetime]

    # Dark sky
    dark_sky_score: Optional[float]
    dark_sky_rating: Optional[str]
```

## Cross-References

- **How solar data feeds condition scoring**: See [Condition Monitoring](../02-product/CONDITION-MONITORING.md)
- **Stargazing activity scheduling**: See [Activity Guidance](../02-product/ACTIVITY-GUIDANCE.md)
- **Moon influence on tides**: See [Tides Integration](./TIDES-INTEGRATION.md)
- **Canonical schemas overview**: See [Data Integrations Overview](./DATA-INTEGRATIONS-OVERVIEW.md)
- **Daily briefing integration**: See [Daily Briefing](../02-product/DAILY-BRIEFING.md)
