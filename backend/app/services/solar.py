from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import httpx
import structlog

from app.redis import redis_client
from app.schemas.conditions import SolarCondition

log = structlog.get_logger()


def _cache_key(lat: float, lon: float, d: date) -> str:
    lat_r = round(lat, 2)
    lon_r = round(lon, 2)
    return f"solar:{lat_r}:{lon_r}:{d.isoformat()}"


def _get_moon_phase(d: date) -> dict:
    try:
        from astral import moon
        phase_value = moon.phase(d)
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

        illumination = round(abs(1 - abs(phase_normalized - 0.5) * 2) * 100, 1)
        return {
            "phase": round(phase_normalized, 3),
            "name": name,
            "illumination_pct": illumination,
        }
    except Exception:
        return {"phase": None, "name": None, "illumination_pct": None}


def _calculate_solar_local(lat: float, lon: float, d: date, tz_name: str = "UTC") -> Optional[SolarCondition]:
    try:
        from astral import LocationInfo
        from astral.sun import sun, golden_hour

        location = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
        s = sun(location.observer, date=d, tzinfo=timezone.utc)

        golden_morning = None
        golden_evening = None
        try:
            gm_start, gm_end = golden_hour(location.observer, date=d, direction=1)
            golden_morning = (gm_start, gm_end)
        except ValueError:
            pass
        try:
            ge_start, ge_end = golden_hour(location.observer, date=d, direction=-1)
            golden_evening = (ge_start, ge_end)
        except ValueError:
            pass

        moon_data = _get_moon_phase(d)
        sunrise = s["sunrise"]
        sunset = s["sunset"]
        day_length = (sunset - sunrise).total_seconds() / 3600

        return SolarCondition(
            date=d,
            location_lat=lat,
            location_lon=lon,
            sunrise=sunrise,
            sunset=sunset,
            solar_noon=s.get("noon"),
            day_length_hours=round(day_length, 2),
            civil_dawn=s.get("dawn"),
            civil_dusk=s.get("dusk"),
            golden_hour_morning_start=golden_morning[0] if golden_morning else None,
            golden_hour_morning_end=golden_morning[1] if golden_morning else None,
            golden_hour_evening_start=golden_evening[0] if golden_evening else None,
            golden_hour_evening_end=golden_evening[1] if golden_evening else None,
            moon_phase=moon_data["phase"],
            moon_phase_name=moon_data["name"],
            moon_illumination_pct=moon_data["illumination_pct"],
        )
    except Exception:
        log.exception("solar_calculation_failed", lat=lat, lon=lon, date=str(d))
        return None


class SolarService:
    async def get_solar(
        self, lat: float, lon: float, d: date, tz_name: str = "Pacific/Auckland"
    ) -> Optional[SolarCondition]:
        cache_k = _cache_key(lat, lon, d)
        try:
            cached = await redis_client.get(cache_k)
            if cached:
                return SolarCondition.model_validate(json.loads(cached))
        except Exception:
            pass

        result = _calculate_solar_local(lat, lon, d, tz_name)
        if result:
            try:
                await redis_client.setex(
                    cache_k, 604800,
                    json.dumps(result.model_dump(mode="json")),
                )
            except Exception:
                pass

        return result

    async def get_solar_range(
        self, lat: float, lon: float, start: date, days: int, tz_name: str = "Pacific/Auckland"
    ) -> list[SolarCondition]:
        results = []
        for i in range(days):
            d = start + timedelta(days=i)
            solar = await self.get_solar(lat, lon, d, tz_name)
            if solar:
                results.append(solar)
        return results

    async def get_aurora_kp(self) -> Optional[dict]:
        """Fetch current and forecast Kp index from NOAA SWPC.

        Kp >= 5 is typically needed for aurora visibility at NZ latitudes (~45°S).
        """
        cache_k = "aurora:kp:current"
        try:
            cached = await redis_client.get(cache_k)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"
                )
                resp.raise_for_status()
                rows = resp.json()

            # First row is the header: ["time_tag", "Kp", "observed", "noaa_scale"]
            if not rows or len(rows) < 2:
                return None

            header = rows[0]
            kp_idx = header.index("Kp") if "Kp" in header else 1
            time_idx = header.index("time_tag") if "time_tag" in header else 0

            data_rows = rows[1:]
            current_kp = float(data_rows[0][kp_idx])

            forecast = [
                {"time": row[time_idx], "kp": float(row[kp_idx])}
                for row in data_rows[:8]
            ]

            result = {
                "current_kp": current_kp,
                "forecast": forecast,
                "is_visible_nz": current_kp >= 5,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            try:
                await redis_client.setex(cache_k, 10800, json.dumps(result))
            except Exception:
                pass

            return result

        except Exception:
            log.exception("aurora_kp_fetch_failed")
            return None


solar_service = SolarService()
