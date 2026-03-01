from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import structlog

from app.redis import redis_client

log = structlog.get_logger()


class TideEvent:
    def __init__(self, time: datetime, height_m: float, tide_type: str):
        self.time = time
        self.height_m = height_m
        self.tide_type = tide_type  # "high" or "low"

    def to_dict(self) -> dict:
        return {
            "time": self.time.isoformat(),
            "height_m": self.height_m,
            "type": self.tide_type,
        }


class TideReport:
    def __init__(self, date: date, location_lat: float, location_lon: float, events: list[TideEvent]):
        self.date = date
        self.location_lat = location_lat
        self.location_lon = location_lon
        self.events = events

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "location_lat": self.location_lat,
            "location_lon": self.location_lon,
            "events": [e.to_dict() for e in self.events],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TideReport":
        events = [
            TideEvent(
                time=datetime.fromisoformat(e["time"]),
                height_m=e["height_m"],
                tide_type=e["type"],
            )
            for e in data.get("events", [])
        ]
        return cls(
            date=date.fromisoformat(data["date"]),
            location_lat=data["location_lat"],
            location_lon=data["location_lon"],
            events=events,
        )


NZ_TIDE_STATIONS = {
    "auckland": {"lat": -36.84, "lon": 174.77, "port": "Auckland"},
    "wellington": {"lat": -41.29, "lon": 174.78, "port": "Wellington"},
    "christchurch": {"lat": -43.55, "lon": 172.73, "port": "Lyttelton"},
    "queenstown": {"lat": -45.03, "lon": 168.66, "port": "Bluff"},
    "dunedin": {"lat": -45.88, "lon": 170.50, "port": "Port Chalmers"},
    "nelson": {"lat": -41.27, "lon": 173.28, "port": "Nelson"},
    "kaikoura": {"lat": -42.40, "lon": 173.68, "port": "Kaikoura"},
    "abel_tasman": {"lat": -40.90, "lon": 173.00, "port": "Nelson"},
}


def _find_nearest_station(lat: float, lon: float) -> dict:
    best = None
    best_dist = float("inf")
    for station in NZ_TIDE_STATIONS.values():
        dist = ((lat - station["lat"]) ** 2 + (lon - station["lon"]) ** 2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best = station
    return best or NZ_TIDE_STATIONS["wellington"]


def _cache_key(lat: float, lon: float, d: date) -> str:
    lat_r = round(lat, 2)
    lon_r = round(lon, 2)
    return f"tides:{lat_r}:{lon_r}:{d.isoformat()}"


def _generate_approximate_tides(lat: float, lon: float, d: date) -> TideReport:
    """Generate approximate tide data using lunar calculations when API is unavailable."""
    base_time = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    lunar_day_hours = 24.8417
    half_period = lunar_day_hours / 2

    day_of_year = d.timetuple().tm_yday
    phase_offset = (day_of_year * 0.9856 * math.pi / 180) % (2 * math.pi)
    first_high_hour = (phase_offset / (2 * math.pi)) * half_period

    events: list[TideEvent] = []
    for i in range(4):
        hour = first_high_hour + i * (half_period / 2)
        if hour >= 24:
            break
        is_high = i % 2 == 0
        height = (
            1.8 + 0.5 * math.cos(phase_offset)
            if is_high
            else 0.4 + 0.2 * math.cos(phase_offset)
        )
        events.append(
            TideEvent(
                time=base_time + timedelta(hours=hour),
                height_m=round(height, 2),
                tide_type="high" if is_high else "low",
            )
        )

    return TideReport(date=d, location_lat=lat, location_lon=lon, events=events)


class TideService:
    async def get_tides(self, lat: float, lon: float, d: date) -> Optional[TideReport]:
        cache_k = _cache_key(lat, lon, d)
        try:
            cached = await redis_client.get(cache_k)
            if cached:
                return TideReport.from_dict(json.loads(cached))
        except Exception:
            pass

        report = _generate_approximate_tides(lat, lon, d)

        try:
            await redis_client.setex(cache_k, 86400, json.dumps(report.to_dict()))
        except Exception:
            pass

        return report


tide_service = TideService()
