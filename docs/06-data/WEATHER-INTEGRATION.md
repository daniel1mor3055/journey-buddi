# Weather Integration

## Overview

Weather data is the single most critical external data source for Journey Buddi. Nearly every activity recommendation, schedule optimization, and real-time alert depends on accurate, granular weather information. This document specifies the providers, data extraction, normalization, caching, and implementation details for weather integration.

## Primary Provider: OpenWeatherMap One Call API 3.0

### Why OpenWeatherMap

- Mature, well-documented API with global coverage
- One Call 3.0 bundles current, hourly (48h), daily (8d), and alerts in a single request
- Supports minute-level precipitation forecasts for the next hour (nowcasting)
- Generous free tier (1,000 calls/day) sufficient for MVP
- Consistent response format across all forecast horizons

### Endpoint

```
GET https://api.openweathermap.org/data/3.0/onecall
  ?lat={lat}
  &lon={lon}
  &exclude={parts}        # optional: current,minutely,hourly,daily,alerts
  &units=metric
  &appid={API_KEY}
```

### Data Available

| Section | Content | Granularity |
|---------|---------|-------------|
| `current` | Real-time conditions | Snapshot |
| `minutely` | Precipitation intensity | Per-minute for 60 min |
| `hourly` | Full forecast | 48 hours, hourly |
| `daily` | Full forecast | 8 days, daily |
| `alerts` | Severe weather warnings | As issued by national agencies |

### Fields We Extract

From each `hourly` entry:

| Field | API Path | Our Schema Field | Notes |
|-------|----------|-----------------|-------|
| Temperature | `hourly[].temp` | `temperature_c` | Already in °C with `units=metric` |
| Feels like | `hourly[].feels_like` | `feels_like_c` | Wind chill / heat index factored |
| Pressure | `hourly[].pressure` | `pressure_hpa` | Sea-level pressure |
| Humidity | `hourly[].humidity` | `humidity_percent` | Percentage 0–100 |
| Dew point | `hourly[].dew_point` | `dew_point_c` | Comfort indicator |
| UV Index | `hourly[].uvi` | `uv_index` | Scale 0–11+ |
| Cloud cover | `hourly[].clouds` | `cloud_cover_pct` | Percentage 0–100 |
| Visibility | `hourly[].visibility` | `visibility_km` | Meters, convert to km |
| Wind speed | `hourly[].wind_speed` | `wind_speed_kmh` | m/s, convert to km/h |
| Wind direction | `hourly[].wind_deg` | `wind_direction_deg` | Degrees 0–360 |
| Wind gust | `hourly[].wind_gust` | `wind_gust_kmh` | m/s, convert to km/h |
| Precip probability | `hourly[].pop` | `precipitation_probability_pct` | 0–1 float, convert to % |
| Rain volume | `hourly[].rain.1h` | `rain_mm` | mm in last hour |
| Snow volume | `hourly[].snow.1h` | `snow_mm` | mm in last hour |
| Weather condition | `hourly[].weather[0]` | `description`, `icon` | Main + description text |

From `daily` entries (additional fields not in hourly):

| Field | API Path | Our Schema Field |
|-------|----------|-----------------|
| Min temperature | `daily[].temp.min` | `temp_min_c` |
| Max temperature | `daily[].temp.max` | `temp_max_c` |
| Summary | `daily[].summary` | `daily_summary` |
| Precipitation total | `daily[].rain` | `daily_rain_mm` |
| Moon phase | `daily[].moon_phase` | `moon_phase` |
| Sunrise/Sunset | `daily[].sunrise`, `daily[].sunset` | `sunrise`, `sunset` |

### Pricing Tiers

| Tier | Daily Calls | Monthly Cost | Journey Buddi Phase |
|------|-------------|-------------|---------------------|
| Free | 1,000/day | $0 | MVP / Development |
| Startup | 10,000/day | ~$45/mo (overage: $0.0015/call) | Early growth |
| Developer | 100,000/day | ~$150/mo | Scale |
| Professional | 1,000,000/day | Custom | Enterprise (future) |

### One Call 3.0 Subscription Note

One Call 3.0 requires subscribing on your OpenWeatherMap account (even for the free tier). The subscription can be paused at any time. The free tier includes 1,000 calls/day with no credit card required.

## Secondary Provider: Open-Meteo (Free Fallback)

### Why Open-Meteo as Fallback

- Completely free for non-commercial use, no API key required
- Hourly forecasts up to 16 days out
- Global coverage via ECMWF, GFS, and other weather models
- Fast responses, high reliability
- Perfect as a zero-cost fallback when OpenWeatherMap is unavailable or rate-limited

### Endpoint

```
GET https://api.open-meteo.com/v1/forecast
  ?latitude={lat}
  &longitude={lon}
  &hourly=temperature_2m,relative_humidity_2m,precipitation_probability,
          precipitation,rain,snowfall,cloud_cover,visibility,
          wind_speed_10m,wind_direction_10m,wind_gusts_10m,
          uv_index,weather_code,apparent_temperature,pressure_msl
  &daily=weather_code,temperature_2m_max,temperature_2m_min,
         sunrise,sunset,precipitation_sum,rain_sum,
         wind_speed_10m_max,wind_gusts_10m_max,uv_index_max
  &timezone=auto
  &forecast_days=8
```

### Field Mapping to Canonical Schema

```python
OPEN_METEO_FIELD_MAP = {
    "temperature_2m": "temperature_c",
    "apparent_temperature": "feels_like_c",
    "relative_humidity_2m": "humidity_percent",
    "pressure_msl": "pressure_hpa",
    "wind_speed_10m": "wind_speed_kmh",       # already in km/h
    "wind_direction_10m": "wind_direction_deg",
    "wind_gusts_10m": "wind_gust_kmh",        # already in km/h
    "precipitation_probability": "precipitation_probability_pct",
    "precipitation": "precipitation_intensity_mmh",
    "cloud_cover": "cloud_cover_pct",
    "visibility": "visibility_km",            # meters, needs / 1000
    "uv_index": "uv_index",
}
```

### Limitations vs OpenWeatherMap

| Feature | OpenWeatherMap | Open-Meteo |
|---------|---------------|------------|
| Minute-by-minute precipitation | Yes (60 min) | No |
| Severe weather alerts | Yes (national agencies) | No |
| Weather icons/descriptions | Yes (rich) | WMO codes only |
| Historical data | Yes (paid) | Yes (free) |
| API key required | Yes | No |
| Rate limiting | 1,000/day free | ~10,000/day (fair use) |

## Tertiary Provider: WeatherAPI.com

### Use Cases

- Marine/surf data (wave height, swell, sea temperature) — not available in OpenWeatherMap
- Additional validation layer when forecasts diverge between providers
- 14-day forecast horizon (vs 8 days for OpenWeatherMap)

### Endpoint

```
GET https://api.weatherapi.com/v1/forecast.json
  ?key={API_KEY}
  &q={lat},{lon}
  &days=14
  &aqi=no
  &alerts=yes
```

### Marine Endpoint

```
GET https://api.weatherapi.com/v1/marine.json
  ?key={API_KEY}
  &q={lat},{lon}
  &days=7
```

Returns: wave height, swell height, swell direction, swell period, water temperature, visibility — critical for kayaking, snorkeling, and boat trip activities.

## Windy.com API (Enhancement Layer)

### Purpose

Windy provides high-resolution wind and precipitation data visualized on maps. The integration is primarily for displaying wind layers on the Mapbox map rather than for backend decision-making.

### Integration Approach

- Embed Windy map tiles as an overlay layer on the Mapbox map.
- Used in the UI to show wind patterns when users are planning marine activities.
- Not a backend data dependency — purely a frontend visualization enhancement.

## Forecast Accuracy by Horizon

Understanding forecast degradation over time is critical for how aggressively the AI agent should adapt plans.

| Horizon | Temperature Accuracy | Precipitation Accuracy | Wind Accuracy | AI Agent Behavior |
|---------|---------------------|----------------------|---------------|-------------------|
| 0–12 hours | ±1°C | 85–90% | ±5 km/h | High confidence. Execute swaps. |
| 12–24 hours | ±2°C | 80–85% | ±10 km/h | Good confidence. Recommend swaps. |
| 24–48 hours | ±2–3°C | 70–80% | ±15 km/h | Moderate confidence. Suggest, don't push. |
| 2–3 days | ±3°C | 60–70% | ±20 km/h | Low confidence. Mention trends. |
| 4–7 days | ±4–5°C | 50–60% | ±25 km/h | Trend-level only. "Looking like rain midweek." |
| 7+ days | ±5°C+ | <50% | ±30 km/h | Ignore for planning. General outlook only. |

### Confidence-Weighted Decisions

The AI agent weights weather data by horizon confidence:

```python
HORIZON_CONFIDENCE = {
    0: 0.95,    # current hour
    6: 0.90,    # 6 hours out
    12: 0.85,   # 12 hours out
    24: 0.80,   # 1 day
    48: 0.70,   # 2 days
    72: 0.55,   # 3 days
    120: 0.40,  # 5 days
    168: 0.25,  # 7 days
}

def get_forecast_confidence(hours_ahead: int) -> float:
    """Interpolate confidence for a given forecast horizon."""
    breakpoints = sorted(HORIZON_CONFIDENCE.keys())
    for i, bp in enumerate(breakpoints):
        if hours_ahead <= bp:
            if i == 0:
                return HORIZON_CONFIDENCE[bp]
            prev_bp = breakpoints[i - 1]
            t = (hours_ahead - prev_bp) / (bp - prev_bp)
            return HORIZON_CONFIDENCE[prev_bp] * (1 - t) + HORIZON_CONFIDENCE[bp] * t
    return 0.2  # beyond 7 days
```

## Caching Strategy

### TTLs by Data Type

| Data Type | Redis TTL | Rationale |
|-----------|-----------|-----------|
| Current conditions | 15 minutes | Users expect "live" data |
| Minutely precipitation | 5 minutes | Nowcasting changes rapidly |
| Hourly forecast (0–12h) | 30 minutes | Short-range forecasts update frequently |
| Hourly forecast (12–48h) | 2 hours | Less volatile, still relevant |
| Daily forecast (2–8 days) | 6 hours | Multi-day outlook changes slowly |
| Severe weather alerts | 5 minutes | Safety-critical, must stay current |
| Marine conditions | 1 hour | Changes moderately |

### Cache Key Structure

```
weather:{provider}:{lat_rounded}:{lon_rounded}:{data_type}:{date_or_hour}
```

Coordinates are rounded to 2 decimal places (~1.1 km precision) to increase cache hit rates — nearby locations share forecasts.

```python
def cache_key(provider: str, lat: float, lon: float, data_type: str, time_bucket: str) -> str:
    lat_r = round(lat, 2)
    lon_r = round(lon, 2)
    return f"weather:{provider}:{lat_r}:{lon_r}:{data_type}:{time_bucket}"
```

### Prefetch Strategy

For each active trip, a Celery beat task runs every 30 minutes:

1. Identify all locations the traveler will visit in the next 48 hours.
2. Check which locations have stale or missing cache entries.
3. Batch-fetch weather for those locations.
4. Write to cache with appropriate TTLs.

This ensures that when the user opens the app or the morning briefing fires, data is already warm in cache.

```python
from celery import shared_task

@shared_task
def prefetch_weather_for_active_trips():
    """Prefetch weather data for all active trip locations."""
    active_trips = get_active_trips()
    for trip in active_trips:
        upcoming_locations = trip.get_locations_next_48h()
        for loc in upcoming_locations:
            cache_k = cache_key("openweathermap", loc.lat, loc.lon, "hourly", "48h")
            if not redis_client.exists(cache_k):
                weather = fetch_and_normalize_weather(loc.lat, loc.lon)
                redis_client.setex(cache_k, 1800, weather.json())
```

## Data Normalization Implementation

### Full Fetch-and-Normalize Flow

```python
import httpx
from datetime import datetime

class OpenWeatherMapAdapter:
    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10.0)

    async def fetch_forecast(self, lat: float, lon: float) -> list[WeatherCondition]:
        params = {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "exclude": "minutely",
            "appid": self.api_key,
        }
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        conditions = []
        for hour in data.get("hourly", []):
            conditions.append(self._normalize_hourly(hour, lat, lon))
        return conditions

    def _normalize_hourly(self, raw: dict, lat: float, lon: float) -> WeatherCondition:
        precip_type = None
        precip_mm = 0.0
        if "rain" in raw:
            precip_type = "rain"
            precip_mm = raw["rain"].get("1h", 0)
        elif "snow" in raw:
            precip_type = "snow"
            precip_mm = raw["snow"].get("1h", 0)

        return WeatherCondition(
            timestamp=datetime.utcfromtimestamp(raw["dt"]),
            location_lat=lat,
            location_lon=lon,
            provider="openweathermap",
            temperature_c=raw["temp"],
            feels_like_c=raw["feels_like"],
            humidity_percent=raw["humidity"],
            pressure_hpa=raw["pressure"],
            wind_speed_kmh=round(raw["wind_speed"] * 3.6, 1),
            wind_direction_deg=raw.get("wind_deg", 0),
            wind_gust_kmh=round(raw.get("wind_gust", 0) * 3.6, 1),
            precipitation_probability_pct=round(raw.get("pop", 0) * 100, 1),
            precipitation_intensity_mmh=precip_mm,
            precipitation_type=precip_type,
            cloud_cover_pct=raw["clouds"],
            visibility_km=round(raw.get("visibility", 10000) / 1000, 1),
            uv_index=raw.get("uvi"),
            description=raw["weather"][0]["description"].capitalize(),
            icon=self._map_icon(raw["weather"][0]["icon"]),
        )

    def _map_icon(self, owm_icon: str) -> str:
        """Map OWM icon codes to Journey Buddi canonical icon names."""
        icon_map = {
            "01d": "clear-day", "01n": "clear-night",
            "02d": "partly-cloudy-day", "02n": "partly-cloudy-night",
            "03d": "cloudy", "03n": "cloudy",
            "04d": "overcast", "04n": "overcast",
            "09d": "rain-showers", "09n": "rain-showers",
            "10d": "rain", "10n": "rain",
            "11d": "thunderstorm", "11n": "thunderstorm",
            "13d": "snow", "13n": "snow",
            "50d": "fog", "50n": "fog",
        }
        return icon_map.get(owm_icon, "unknown")


class OpenMeteoAdapter:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def fetch_forecast(self, lat: float, lon: float) -> list[WeatherCondition]:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ",".join([
                "temperature_2m", "apparent_temperature", "relative_humidity_2m",
                "precipitation_probability", "precipitation", "rain", "snowfall",
                "cloud_cover", "visibility", "wind_speed_10m", "wind_direction_10m",
                "wind_gusts_10m", "uv_index", "weather_code", "pressure_msl",
            ]),
            "timezone": "UTC",
            "forecast_days": 8,
        }
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        hourly = data["hourly"]
        conditions = []
        for i, ts in enumerate(hourly["time"]):
            conditions.append(WeatherCondition(
                timestamp=datetime.fromisoformat(ts),
                location_lat=lat,
                location_lon=lon,
                provider="open-meteo",
                temperature_c=hourly["temperature_2m"][i],
                feels_like_c=hourly["apparent_temperature"][i],
                humidity_percent=hourly["relative_humidity_2m"][i],
                pressure_hpa=hourly["pressure_msl"][i],
                wind_speed_kmh=hourly["wind_speed_10m"][i],
                wind_direction_deg=hourly["wind_direction_10m"][i],
                wind_gust_kmh=hourly["wind_gusts_10m"][i] or 0,
                precipitation_probability_pct=hourly["precipitation_probability"][i],
                precipitation_intensity_mmh=hourly["precipitation"][i],
                precipitation_type=self._classify_precip(
                    hourly["rain"][i], hourly["snowfall"][i]
                ),
                cloud_cover_pct=hourly["cloud_cover"][i],
                visibility_km=round(hourly["visibility"][i] / 1000, 1),
                uv_index=hourly["uv_index"][i],
                description=self._wmo_to_description(hourly["weather_code"][i]),
                icon=self._wmo_to_icon(hourly["weather_code"][i]),
            ))
        return conditions

    def _classify_precip(self, rain_mm: float, snow_mm: float) -> str | None:
        if snow_mm and snow_mm > 0:
            return "snow"
        if rain_mm and rain_mm > 0:
            return "rain"
        return None

    def _wmo_to_description(self, code: int) -> str:
        wmo_descriptions = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
            3: "Overcast", 45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            80: "Slight rain showers", 81: "Moderate rain showers",
            82: "Violent rain showers", 95: "Thunderstorm",
            96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
        }
        return wmo_descriptions.get(code, "Unknown")

    def _wmo_to_icon(self, code: int) -> str:
        if code == 0:
            return "clear-day"
        if code <= 2:
            return "partly-cloudy-day"
        if code == 3:
            return "overcast"
        if code in (45, 48):
            return "fog"
        if code in (51, 53, 55):
            return "drizzle"
        if code in (61, 63, 65, 80, 81, 82):
            return "rain"
        if code in (71, 73, 75):
            return "snow"
        if code >= 95:
            return "thunderstorm"
        return "unknown"
```

## Weather Service Orchestrator

The weather service orchestrates providers, caching, and fallbacks:

```python
class WeatherService:
    def __init__(self, settings: ExternalAPISettings, redis: Redis):
        self.primary = OpenWeatherMapAdapter(settings.openweathermap_api_key)
        self.fallback = OpenMeteoAdapter()
        self.redis = redis
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=300)

    async def get_forecast(self, lat: float, lon: float) -> list[WeatherCondition]:
        cache_k = cache_key("weather", lat, lon, "hourly", "48h")
        cached = self.redis.get(cache_k)
        if cached:
            return [WeatherCondition.model_validate_json(c) for c in json.loads(cached)]

        if self.circuit_breaker.can_execute():
            try:
                conditions = await self.primary.fetch_forecast(lat, lon)
                self.circuit_breaker.record_success()
                self._cache_conditions(cache_k, conditions, ttl=1800)
                return conditions
            except Exception:
                self.circuit_breaker.record_failure()

        conditions = await self.fallback.fetch_forecast(lat, lon)
        self._cache_conditions(cache_k, conditions, ttl=1800)
        return conditions

    def _cache_conditions(self, key: str, conditions: list[WeatherCondition], ttl: int):
        self.redis.setex(key, ttl, json.dumps([c.model_dump_json() for c in conditions]))
```

## NZ-Specific Considerations

- **MetService NZ**: For severe weather warnings specific to New Zealand, supplement OpenWeatherMap alerts with MetService RSS feeds (publicly available).
- **Mountain weather**: Altitude significantly affects NZ mountain weather. Apply a lapse rate correction of approximately -6.5°C per 1,000m elevation gain for mountain activities.
- **Microclimates**: NZ has extreme microclimate variation (e.g., Milford Sound gets 6,000mm rain/year while Queenstown, 100km away, gets 800mm). Always fetch weather per-location, never extrapolate between towns.
- **Four seasons in one day**: Common in NZ. The system should watch for rapid condition changes (pressure drops >3 hPa/hour) and trigger alerts.

## Cross-References

- **How weather feeds condition scoring**: See [Condition Monitoring](../02-product/CONDITION-MONITORING.md)
- **Activity weather profiles**: See [Activity Guidance](../02-product/ACTIVITY-GUIDANCE.md)
- **Canonical schemas**: See [Data Integrations Overview](./DATA-INTEGRATIONS-OVERVIEW.md)
- **Data model storage**: See [Data Model](../05-architecture/DATA-MODEL.md)
