from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

import httpx
import structlog

from app.config import get_settings
from app.redis import redis_client
from app.schemas.conditions import WeatherCondition, DailyWeatherSummary

log = structlog.get_logger()
settings = get_settings()

HORIZON_CONFIDENCE = {
    0: 0.95,
    6: 0.90,
    12: 0.85,
    24: 0.80,
    48: 0.70,
    72: 0.55,
    120: 0.40,
    168: 0.25,
}


def get_forecast_confidence(hours_ahead: int) -> float:
    breakpoints = sorted(HORIZON_CONFIDENCE.keys())
    for i, bp in enumerate(breakpoints):
        if hours_ahead <= bp:
            if i == 0:
                return HORIZON_CONFIDENCE[bp]
            prev_bp = breakpoints[i - 1]
            t = (hours_ahead - prev_bp) / (bp - prev_bp)
            return HORIZON_CONFIDENCE[prev_bp] * (1 - t) + HORIZON_CONFIDENCE[bp] * t
    return 0.2


def _cache_key(lat: float, lon: float, data_type: str) -> str:
    lat_r = round(lat, 2)
    lon_r = round(lon, 2)
    return f"weather:{lat_r}:{lon_r}:{data_type}"


WMO_DESCRIPTIONS = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy",
    3: "Overcast", 45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers",
    82: "Violent rain showers", 95: "Thunderstorm",
    96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


def _wmo_to_icon(code: int) -> str:
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


class OpenMeteoAdapter:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)

    async def fetch_hourly(self, lat: float, lon: float, days: int = 8) -> list[WeatherCondition]:
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
            "forecast_days": days,
        }
        resp = await self.client.get(self.BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        hourly = data["hourly"]

        conditions = []
        for i, ts in enumerate(hourly["time"]):
            precip_type = None
            rain_val = hourly["rain"][i] or 0
            snow_val = hourly["snowfall"][i] or 0
            if snow_val > 0:
                precip_type = "snow"
            elif rain_val > 0:
                precip_type = "rain"

            conditions.append(WeatherCondition(
                timestamp=datetime.fromisoformat(ts).replace(tzinfo=timezone.utc),
                location_lat=lat,
                location_lon=lon,
                provider="open-meteo",
                temperature_c=hourly["temperature_2m"][i] or 0,
                feels_like_c=hourly["apparent_temperature"][i] or 0,
                humidity_percent=hourly["relative_humidity_2m"][i] or 0,
                pressure_hpa=hourly["pressure_msl"][i] or 0,
                wind_speed_kmh=hourly["wind_speed_10m"][i] or 0,
                wind_direction_deg=int(hourly["wind_direction_10m"][i] or 0),
                wind_gust_kmh=hourly["wind_gusts_10m"][i] or 0,
                precipitation_probability_pct=hourly["precipitation_probability"][i] or 0,
                precipitation_intensity_mmh=hourly["precipitation"][i] or 0,
                precipitation_type=precip_type,
                cloud_cover_pct=hourly["cloud_cover"][i] or 0,
                visibility_km=round((hourly["visibility"][i] or 10000) / 1000, 1),
                uv_index=hourly["uv_index"][i],
                description=WMO_DESCRIPTIONS.get(hourly["weather_code"][i] or 0, "Unknown"),
                icon=_wmo_to_icon(hourly["weather_code"][i] or 0),
            ))
        return conditions

    async def fetch_daily(self, lat: float, lon: float, days: int = 8) -> list[DailyWeatherSummary]:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ",".join([
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "sunrise", "sunset", "precipitation_sum", "precipitation_probability_max",
                "wind_speed_10m_max", "wind_gusts_10m_max", "uv_index_max",
            ]),
            "timezone": "UTC",
            "forecast_days": days,
        }
        resp = await self.client.get(self.BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        daily = data["daily"]

        summaries = []
        for i, d in enumerate(daily["time"]):
            from datetime import date as date_cls
            dt = date_cls.fromisoformat(d)
            code = daily["weather_code"][i] or 0

            sunrise_val = daily.get("sunrise", [None] * (i + 1))[i]
            sunset_val = daily.get("sunset", [None] * (i + 1))[i]

            summaries.append(DailyWeatherSummary(
                date=dt,
                temp_min_c=daily["temperature_2m_min"][i] or 0,
                temp_max_c=daily["temperature_2m_max"][i] or 0,
                description=WMO_DESCRIPTIONS.get(code, "Unknown"),
                icon=_wmo_to_icon(code),
                precipitation_probability_pct=daily["precipitation_probability_max"][i] or 0,
                wind_speed_max_kmh=daily["wind_speed_10m_max"][i] or 0,
                uv_index_max=daily["uv_index_max"][i],
                sunrise=datetime.fromisoformat(sunrise_val).replace(tzinfo=timezone.utc) if sunrise_val else None,
                sunset=datetime.fromisoformat(sunset_val).replace(tzinfo=timezone.utc) if sunset_val else None,
            ))
        return summaries

    async def close(self):
        await self.client.aclose()


OWM_ICON_MAP = {
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


class OpenWeatherMapAdapter:
    ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"
    CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=15.0)

    async def fetch_hourly(self, lat: float, lon: float, days: int = 5) -> list[WeatherCondition]:
        """Try One Call 3.0 first; fall back to free 2.5 forecast endpoint."""
        try:
            return await self._fetch_onecall(lat, lon)
        except Exception:
            log.warning("owm_onecall_failed_falling_back_to_25", lat=lat, lon=lon)
            return await self._fetch_forecast25(lat, lon, days)

    async def _fetch_onecall(self, lat: float, lon: float) -> list[WeatherCondition]:
        params = {
            "lat": lat, "lon": lon,
            "units": "metric", "exclude": "minutely",
            "appid": self.api_key,
        }
        resp = await self.client.get(self.ONECALL_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        conditions = []
        for hour in data.get("hourly", []):
            precip_type = None
            precip_mm = 0.0
            if "rain" in hour:
                precip_type = "rain"
                precip_mm = hour["rain"].get("1h", 0)
            elif "snow" in hour:
                precip_type = "snow"
                precip_mm = hour["snow"].get("1h", 0)

            conditions.append(WeatherCondition(
                timestamp=datetime.utcfromtimestamp(hour["dt"]).replace(tzinfo=timezone.utc),
                location_lat=lat, location_lon=lon,
                provider="openweathermap",
                temperature_c=hour["temp"],
                feels_like_c=hour["feels_like"],
                humidity_percent=hour["humidity"],
                pressure_hpa=hour["pressure"],
                wind_speed_kmh=round(hour["wind_speed"] * 3.6, 1),
                wind_direction_deg=int(hour.get("wind_deg", 0)),
                wind_gust_kmh=round(hour.get("wind_gust", 0) * 3.6, 1),
                precipitation_probability_pct=round(hour.get("pop", 0) * 100, 1),
                precipitation_intensity_mmh=precip_mm,
                precipitation_type=precip_type,
                cloud_cover_pct=hour["clouds"],
                visibility_km=round(hour.get("visibility", 10000) / 1000, 1),
                uv_index=hour.get("uvi"),
                description=hour["weather"][0]["description"].capitalize(),
                icon=OWM_ICON_MAP.get(hour["weather"][0]["icon"], "unknown"),
            ))
        return conditions

    async def _fetch_forecast25(self, lat: float, lon: float, days: int) -> list[WeatherCondition]:
        """Free 2.5 forecast — 3-hourly for 5 days, no subscription needed."""
        params = {
            "lat": lat, "lon": lon,
            "units": "metric", "cnt": min(days * 8, 40),
            "appid": self.api_key,
        }
        resp = await self.client.get(self.FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        conditions = []
        for entry in data.get("list", []):
            precip_type = None
            precip_mm = 0.0
            if "rain" in entry:
                precip_type = "rain"
                precip_mm = entry["rain"].get("3h", 0) / 3
            elif "snow" in entry:
                precip_type = "snow"
                precip_mm = entry["snow"].get("3h", 0) / 3

            conditions.append(WeatherCondition(
                timestamp=datetime.utcfromtimestamp(entry["dt"]).replace(tzinfo=timezone.utc),
                location_lat=lat, location_lon=lon,
                provider="openweathermap-2.5",
                temperature_c=entry["main"]["temp"],
                feels_like_c=entry["main"]["feels_like"],
                humidity_percent=entry["main"]["humidity"],
                pressure_hpa=entry["main"]["pressure"],
                wind_speed_kmh=round(entry["wind"]["speed"] * 3.6, 1),
                wind_direction_deg=int(entry["wind"].get("deg", 0)),
                wind_gust_kmh=round(entry["wind"].get("gust", 0) * 3.6, 1),
                precipitation_probability_pct=round(entry.get("pop", 0) * 100, 1),
                precipitation_intensity_mmh=precip_mm,
                precipitation_type=precip_type,
                cloud_cover_pct=entry["clouds"]["all"],
                visibility_km=round(entry.get("visibility", 10000) / 1000, 1),
                uv_index=None,
                description=entry["weather"][0]["description"].capitalize(),
                icon=OWM_ICON_MAP.get(entry["weather"][0]["icon"], "unknown"),
            ))
        return conditions

    async def close(self):
        await self.client.aclose()


class WeatherService:
    def __init__(self):
        self.open_meteo = OpenMeteoAdapter()
        owm_key = settings.openweathermap_api_key
        self.owm = OpenWeatherMapAdapter(owm_key) if owm_key else None

    async def get_hourly_forecast(
        self, lat: float, lon: float, days: int = 8, use_cache: bool = True
    ) -> list[WeatherCondition]:
        cache_k = _cache_key(lat, lon, f"hourly:{days}d")

        if use_cache:
            try:
                cached = await redis_client.get(cache_k)
                if cached:
                    items = json.loads(cached)
                    return [WeatherCondition.model_validate(c) for c in items]
            except Exception:
                log.warning("weather_cache_read_failed", key=cache_k)

        # OWM primary → Open-Meteo fallback
        conditions: list[WeatherCondition] = []
        if self.owm:
            try:
                conditions = await self.owm.fetch_hourly(lat, lon, days)
                log.debug("weather_fetched_from_owm", lat=lat, lon=lon, count=len(conditions))
            except Exception:
                log.warning("owm_fetch_failed_using_open_meteo", lat=lat, lon=lon)

        if not conditions:
            try:
                conditions = await self.open_meteo.fetch_hourly(lat, lon, days)
                log.debug("weather_fetched_from_open_meteo", lat=lat, lon=lon, count=len(conditions))
            except Exception:
                log.exception("weather_fetch_failed_all_providers", lat=lat, lon=lon)
                return []

        try:
            await redis_client.setex(
                cache_k, 1800,
                json.dumps([c.model_dump(mode="json") for c in conditions]),
            )
        except Exception:
            log.warning("weather_cache_write_failed", key=cache_k)

        return conditions

    async def get_daily_forecast(
        self, lat: float, lon: float, days: int = 8, use_cache: bool = True
    ) -> list[DailyWeatherSummary]:
        cache_k = _cache_key(lat, lon, f"daily:{days}d")

        if use_cache:
            try:
                cached = await redis_client.get(cache_k)
                if cached:
                    items = json.loads(cached)
                    return [DailyWeatherSummary.model_validate(c) for c in items]
            except Exception:
                log.warning("daily_cache_read_failed", key=cache_k)

        try:
            summaries = await self.open_meteo.fetch_daily(lat, lon, days)
            try:
                await redis_client.setex(
                    cache_k, 21600,
                    json.dumps([s.model_dump(mode="json") for s in summaries]),
                )
            except Exception:
                log.warning("daily_cache_write_failed", key=cache_k)
            return summaries
        except Exception:
            log.exception("daily_fetch_failed", lat=lat, lon=lon)
            return []

    async def get_conditions_for_datetime(
        self, lat: float, lon: float, target_dt: datetime
    ) -> Optional[WeatherCondition]:
        conditions = await self.get_hourly_forecast(lat, lon)
        if not conditions:
            return None

        target_utc = target_dt.replace(tzinfo=timezone.utc) if target_dt.tzinfo is None else target_dt
        best = None
        best_delta = float("inf")
        for c in conditions:
            delta = abs((c.timestamp - target_utc).total_seconds())
            if delta < best_delta:
                best_delta = delta
                best = c
        return best


weather_service = WeatherService()
