# Data Integrations Overview

## Purpose

Journey Buddi's adaptive intelligence depends on real-time environmental data from multiple external sources. This document catalogs every external API integration, describes how data flows through the system, and establishes the strategies for key management, rate limiting, error handling, cost control, and data normalization.

## External API Inventory

### Weather Data

| Provider | Purpose | Free Tier | Paid Tier | Priority |
|----------|---------|-----------|-----------|----------|
| OpenWeatherMap (One Call 3.0) | Primary weather: hourly/daily forecasts, alerts | 1,000 calls/day | $0.0015/call beyond free | Primary |
| Open-Meteo | Free fallback weather data | Unlimited (non-commercial) | N/A | Fallback |
| WeatherAPI.com | Secondary weather + marine data | 1M calls/month (free) | From $9/mo | Secondary |
| Windy.com API | Advanced wind/precipitation visualization | Limited | Contact for pricing | Enhancement |

### Tides & Marine

| Provider | Purpose | Free Tier | Paid Tier | Priority |
|----------|---------|-----------|-----------|----------|
| WorldTides API | Global tide predictions | 50 credits/day free | From $5/mo (500 credits/day) | Primary |
| NIWA (NZ Tides) | NZ-specific tide stations | Free public data | N/A | NZ-specific supplement |

### Solar, Celestial & Aurora

| Provider | Purpose | Free Tier | Paid Tier | Priority |
|----------|---------|-----------|-----------|----------|
| sunrise-sunset.org | Sunrise/sunset/golden hour | Unlimited, free | N/A | Primary |
| NOAA SWPC | Aurora/geomagnetic forecasting (Kp index) | Free (public data) | N/A | Primary |
| USNO / Astronomy API | Moon phase, rise/set times | Free | N/A | Primary |
| OpenUV | UV index by location | 50 requests/day free | Plans from $10/mo | Primary |

### Maps & Routing

| Provider | Purpose | Free Tier | Paid Tier | Priority |
|----------|---------|-----------|-----------|----------|
| Mapbox | Map display, directions, geocoding | 100K tile loads, 100K direction requests/mo | Pay-as-you-go | Primary |
| OSRM (self-hosted) | Open-source routing fallback | Free (self-hosted) | Server cost only | Fallback |
| Overpass API (OpenStreetMap) | POI discovery, trail data | Free | N/A | Primary |
| Google Places API | Rich POI data, photos, reviews | $200/mo credit | $0.032/request | Enhancement |

### Wildlife & Environmental

| Provider | Purpose | Free Tier | Paid Tier | Priority |
|----------|---------|-----------|-----------|----------|
| iNaturalist API | Wildlife observation data | Free | N/A | Supplement |
| DOC NZ (Web scraping / RSS) | Trail status, conservation alerts | Free (public) | N/A | NZ-specific |
| MetService NZ | NZ-specific severe weather alerts | Free (public) | N/A | NZ-specific |

## Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL DATA SOURCES                               │
│                                                                              │
│  OpenWeatherMap  WorldTides  NOAA  Mapbox  sunrise-sunset  iNaturalist      │
│  Open-Meteo      NIWA       OpenUV  OSRM   Astronomy API   DOC NZ          │
└───────┬────────────┬──────────┬───────┬──────────┬───────────┬──────────────┘
        │            │          │       │          │           │
        ▼            ▼          ▼       ▼          ▼           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL DATA SERVICE                                  │
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                 │
│  │  API Client    │  │  Rate Limiter  │  │  Circuit       │                 │
│  │  Registry      │  │  (per-provider)│  │  Breaker       │                 │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                 │
│          │                   │                    │                           │
│          ▼                   ▼                    ▼                           │
│  ┌─────────────────────────────────────────────────────────┐                 │
│  │              DATA NORMALIZATION LAYER                    │                 │
│  │                                                         │                 │
│  │  Raw API Response → Provider Adapter → Canonical Schema │                 │
│  └────────────────────────────┬────────────────────────────┘                 │
│                               │                                              │
└───────────────────────────────┼──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          CACHING LAYER                                       │
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                 │
│  │  L1: In-Memory │  │  L2: Redis     │  │  L3: Postgres  │                 │
│  │  (hot data)    │  │  (active trips)│  │  (historical)  │                 │
│  │  TTL: seconds  │  │  TTL: minutes  │  │  TTL: permanent│                 │
│  └────────────────┘  └────────────────┘  └────────────────┘                 │
│                                                                              │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        CONSUMERS                                             │
│                                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                 │
│  │  Condition     │  │  AI Agent      │  │  Itinerary     │                 │
│  │  Service       │  │  (Buddi)       │  │  Service       │                 │
│  │                │  │                │  │                │                 │
│  │  Scoring &     │  │  Decision      │  │  Scheduling &  │                 │
│  │  Alerts        │  │  Making        │  │  Optimization  │                 │
│  └────────────────┘  └────────────────┘  └────────────────┘                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Request Lifecycle

1. **Consumer requests data** — e.g., the Condition Service needs weather for Queenstown at 14:00 tomorrow.
2. **Cache lookup** — L1 memory → L2 Redis. If a fresh-enough record exists, return it immediately.
3. **Cache miss** — The External Data Service issues an API call through the rate limiter.
4. **Rate limiter check** — If the provider's rate budget is exhausted, the request is queued or falls back to a secondary provider.
5. **Circuit breaker** — If the provider has been failing (>50% error rate in the last 5 minutes), the circuit opens and the request is routed to the fallback provider.
6. **Raw response** — Passed through the provider-specific adapter for normalization into the canonical schema.
7. **Cache write** — The normalized result is written to L2 (Redis) and L3 (Postgres) with appropriate TTLs.
8. **Return** — The normalized data is returned to the consumer.

## API Key Management

### Strategy

All API keys are stored as environment variables and accessed through a centralized `settings` module. No keys are ever committed to source control.

```python
from pydantic_settings import BaseSettings

class ExternalAPISettings(BaseSettings):
    """Centralized external API key configuration."""

    # Weather
    openweathermap_api_key: str
    weatherapi_key: str = ""  # optional fallback

    # Tides
    worldtides_api_key: str

    # Maps
    mapbox_access_token: str
    google_places_api_key: str = ""  # optional enhancement

    # UV
    openuv_api_key: str

    class Config:
        env_file = ".env"
        env_prefix = "JOURNEY_"
```

### Key Rotation

- Keys are rotated quarterly via environment variable updates on Railway.
- Old keys are revoked within 24 hours of rotation.
- A Celery health-check task validates all keys daily and alerts if any return 401/403.

### Per-Environment Keys

| Environment | Key Source | Rate Tier |
|-------------|-----------|-----------|
| Development | Developer's personal free-tier keys | Free tier limits |
| Staging | Shared staging keys (low-rate paid) | Paid, low-volume |
| Production | Production keys (full-rate paid) | Paid, production-volume |

## Rate Limiting Strategy

### Per-Provider Rate Budgets

Each provider has a configured rate budget, tracked in Redis with a sliding window counter.

```python
RATE_LIMITS = {
    "openweathermap": {
        "calls_per_minute": 60,
        "calls_per_day": 1000,       # free tier
        "burst_allowance": 10,       # allow short bursts
    },
    "worldtides": {
        "calls_per_minute": 10,
        "calls_per_day": 50,         # free tier
        "burst_allowance": 5,
    },
    "mapbox_directions": {
        "calls_per_minute": 300,
        "calls_per_day": 100_000,    # free tier
        "burst_allowance": 50,
    },
    "sunrise_sunset": {
        "calls_per_minute": 30,
        "calls_per_day": None,       # no daily limit
        "burst_allowance": 10,
    },
    "openuv": {
        "calls_per_minute": 5,
        "calls_per_day": 50,         # free tier
        "burst_allowance": 2,
    },
}
```

### Rate Budget Enforcement

```python
import redis
import time

class RateLimiter:
    """Sliding window rate limiter backed by Redis."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def check_and_consume(self, provider: str, window: str = "minute") -> bool:
        config = RATE_LIMITS[provider]
        if window == "minute":
            limit = config["calls_per_minute"]
            window_seconds = 60
        elif window == "day":
            limit = config["calls_per_day"]
            if limit is None:
                return True
            window_seconds = 86400

        key = f"ratelimit:{provider}:{window}:{int(time.time()) // window_seconds}"
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, window_seconds)
        return current <= limit

    def wait_or_fallback(self, provider: str) -> str:
        """Returns the provider to use — original or fallback."""
        if self.check_and_consume(provider, "minute") and self.check_and_consume(provider, "day"):
            return provider
        fallback = FALLBACK_PROVIDERS.get(provider)
        if fallback and self.check_and_consume(fallback, "minute"):
            return fallback
        raise RateLimitExhausted(f"Both {provider} and fallback exhausted")
```

### Request Batching

To minimize API calls, the system batches requests:
- **Weather**: Fetch the full 48-hour hourly + 8-day daily forecast in a single One Call request rather than individual time-slot queries.
- **Tides**: Request a full 7-day tide table per station in one call.
- **Solar**: Compute sunrise/sunset for all relevant dates per location in a batch.

## Error Handling & Fallback Strategy

### Circuit Breaker Pattern

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"         # normal operation
    OPEN = "open"             # failing, use fallback
    HALF_OPEN = "half_open"   # testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout  # seconds
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True  # HALF_OPEN: allow one test request
```

### Fallback Chain

Each data type has a defined fallback chain:

| Data Type | Primary | Fallback 1 | Fallback 2 | Last Resort |
|-----------|---------|------------|------------|-------------|
| Weather | OpenWeatherMap | Open-Meteo | WeatherAPI.com | Serve stale cache (flagged) |
| Tides | WorldTides | NIWA (NZ only) | — | Serve stale cache (flagged) |
| Solar | sunrise-sunset.org | Manual calculation (pyephem) | — | Compute locally |
| Aurora | NOAA SWPC | — | — | Disable aurora alerts |
| Maps/Routing | Mapbox | OSRM (self-hosted) | — | Show straight-line estimate |
| UV Index | OpenUV | OpenWeatherMap (includes UV) | — | Omit UV from briefing |
| POI Data | Overpass API | Google Places | — | Use cached POI database |

### Stale Data Policy

When all providers are unavailable:
- Serve the most recent cached data with a `stale: true` flag and a `fetched_at` timestamp.
- The AI agent includes a caveat in its briefing: *"Note: weather data is from {X} hours ago — check conditions before heading out."*
- Never present stale data older than 24 hours for weather or 48 hours for tides without a prominent warning.

## Cost Estimates

### Monthly Cost at MVP Scale (50 active trips, ~200 API calls/trip/day)

| Provider | Estimated Calls/Month | Free Tier Covers | Estimated Cost |
|----------|-----------------------|-----------------|----------------|
| OpenWeatherMap | ~10,000 | 1,000/day (30K/mo) | $0 (within free tier) |
| Open-Meteo | ~2,000 (fallback) | Unlimited | $0 |
| WorldTides | ~1,500 | 50/day (1,500/mo) | $0 (tight fit) |
| sunrise-sunset.org | ~3,000 | Unlimited | $0 |
| NOAA SWPC | ~1,000 | Unlimited (public) | $0 |
| OpenUV | ~1,500 | 50/day (1,500/mo) | $0 (tight fit) |
| Mapbox | ~15,000 | 100K/mo | $0 |
| Overpass API | ~2,000 | Unlimited | $0 |
| **Total MVP** | | | **$0/mo** |

### Scaling Cost (500 active trips)

| Provider | Estimated Calls/Month | Estimated Cost |
|----------|-----------------------|----------------|
| OpenWeatherMap | ~100,000 | ~$105/mo |
| WorldTides | ~15,000 | ~$10/mo |
| OpenUV | ~15,000 | ~$10/mo |
| Mapbox | ~150,000 | ~$75/mo |
| Google Places | ~10,000 | ~$320/mo (if used) |
| **Total at scale** | | **~$200–520/mo** |

The key cost driver at scale is Google Places. The strategy is to build a local POI cache from Overpass (free) and only use Google Places for enrichment (photos, reviews) on demand.

## Data Normalization

### Problem

Each API returns data in a different format, with different units, time formats, and field names. The normalization layer converts everything into canonical Journey Buddi schemas.

### Canonical Schemas

#### WeatherCondition

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WeatherCondition(BaseModel):
    """Canonical weather data point after normalization."""
    timestamp: datetime
    location_lat: float
    location_lon: float
    provider: str
    temperature_c: float
    feels_like_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_kmh: float
    wind_direction_deg: int
    wind_gust_kmh: Optional[float]
    precipitation_probability_pct: float
    precipitation_intensity_mmh: float
    precipitation_type: Optional[str]   # "rain", "snow", "sleet", None
    cloud_cover_pct: float
    visibility_km: float
    uv_index: Optional[float]
    description: str                     # human-readable, e.g. "Partly cloudy"
    icon: str                            # normalized icon code
```

#### TideCondition

```python
class TideEvent(BaseModel):
    """A single high or low tide."""
    timestamp: datetime
    type: str               # "high" or "low"
    height_m: float
    station_id: str
    station_name: str

class TideCondition(BaseModel):
    """Tide data for a location and date range."""
    station_id: str
    station_name: str
    location_lat: float
    location_lon: float
    provider: str
    events: list[TideEvent]
    datum: str              # e.g. "MSL", "LAT"
```

#### SolarCondition

```python
class SolarCondition(BaseModel):
    """Solar and celestial data for a date and location."""
    date: datetime
    location_lat: float
    location_lon: float
    sunrise: datetime
    sunset: datetime
    solar_noon: datetime
    day_length_hours: float
    golden_hour_morning_start: datetime
    golden_hour_morning_end: datetime
    golden_hour_evening_start: datetime
    golden_hour_evening_end: datetime
    moon_phase: float           # 0.0 = new, 0.5 = full, 1.0 = new
    moon_phase_name: str        # "Waxing Crescent", "Full Moon", etc.
    moonrise: Optional[datetime]
    moonset: Optional[datetime]
    aurora_kp_index: Optional[float]
    aurora_probability_pct: Optional[float]
```

### Provider Adapters

Each provider has an adapter that implements a common interface:

```python
from abc import ABC, abstractmethod

class WeatherProviderAdapter(ABC):
    """Interface all weather provider adapters must implement."""

    @abstractmethod
    async def fetch_forecast(self, lat: float, lon: float) -> list[WeatherCondition]:
        """Fetch hourly forecast and return normalized data."""
        ...

    @abstractmethod
    async def fetch_current(self, lat: float, lon: float) -> WeatherCondition:
        """Fetch current conditions and return normalized data."""
        ...

class OpenWeatherMapAdapter(WeatherProviderAdapter):
    async def fetch_forecast(self, lat: float, lon: float) -> list[WeatherCondition]:
        raw = await self._call_api(f"/onecall?lat={lat}&lon={lon}&units=metric")
        return [self._normalize_hourly(h, lat, lon) for h in raw["hourly"]]

    def _normalize_hourly(self, raw: dict, lat: float, lon: float) -> WeatherCondition:
        return WeatherCondition(
            timestamp=datetime.utcfromtimestamp(raw["dt"]),
            location_lat=lat,
            location_lon=lon,
            provider="openweathermap",
            temperature_c=raw["temp"],
            feels_like_c=raw["feels_like"],
            humidity_percent=raw["humidity"],
            pressure_hpa=raw["pressure"],
            wind_speed_kmh=raw["wind_speed"] * 3.6,  # m/s to km/h
            wind_direction_deg=raw["wind_deg"],
            wind_gust_kmh=raw.get("wind_gust", 0) * 3.6,
            precipitation_probability_pct=raw.get("pop", 0) * 100,
            precipitation_intensity_mmh=raw.get("rain", {}).get("1h", 0),
            precipitation_type=self._classify_precip(raw),
            cloud_cover_pct=raw["clouds"],
            visibility_km=raw.get("visibility", 10000) / 1000,
            uv_index=raw.get("uvi"),
            description=raw["weather"][0]["description"],
            icon=self._map_icon(raw["weather"][0]["icon"]),
        )
```

### Unit Standardization

All data is stored in these canonical units:

| Measurement | Canonical Unit | Conversions Applied |
|-------------|---------------|---------------------|
| Temperature | °C | °F → °C: `(f - 32) * 5/9` |
| Wind speed | km/h | m/s → km/h: `* 3.6`, knots → km/h: `* 1.852`, mph → km/h: `* 1.609` |
| Pressure | hPa | Identical to mbar; inHg → hPa: `* 33.8639` |
| Visibility | km | meters → km: `/ 1000`, miles → km: `* 1.609` |
| Precipitation | mm/h | inches/h → mm/h: `* 25.4` |
| Tide height | meters | feet → meters: `* 0.3048` |
| Distance | km | miles → km: `* 1.609` |
| Timestamps | UTC (ISO 8601) | Unix epoch → ISO 8601 datetime |

## Cross-References

- **Data freshness requirements**: See [Condition Monitoring](../02-product/CONDITION-MONITORING.md)
- **How the AI agent uses this data**: See [Decision Engine](../03-ai/DECISION-ENGINE.md)
- **Data model for storage**: See [Data Model](../05-architecture/DATA-MODEL.md)
- **Caching infrastructure**: See [System Architecture](../05-architecture/SYSTEM-ARCHITECTURE.md)
- **Individual integration specs**: See sibling files in this directory
