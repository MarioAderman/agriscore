"""Step 3a: Fetch climate data from Open-Meteo and NASA POWER."""

import logging
from datetime import datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


async def fetch_climate_data(
    latitude: float,
    longitude: float,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    """Fetch climate data: temperature, precipitation, ET0 from Open-Meteo
    and soil moisture from NASA POWER.

    Returns dict with avg_temperature, total_precipitation, et0, soil_moisture.
    """
    now = datetime.now(timezone.utc)
    if not date_to:
        # Open-Meteo archive has ~5 day lag
        date_to = (now - timedelta(days=5)).strftime("%Y-%m-%d")
    if not date_from:
        date_from = (now - timedelta(days=365)).strftime("%Y-%m-%d")

    # Fetch Open-Meteo and NASA POWER in parallel
    async with httpx.AsyncClient(timeout=30) as client:
        # Open-Meteo: temperature, precipitation, ET0
        meteo_resp = await client.get(
            OPEN_METEO_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "start_date": date_from,
                "end_date": date_to,
                "daily": "temperature_2m_mean,precipitation_sum,et0_fao_evapotranspiration",
                "timezone": "America/Mexico_City",
            },
        )
        meteo_resp.raise_for_status()
        meteo_data = meteo_resp.json()

        # NASA POWER: soil moisture (GWETROOT)
        # NASA POWER uses YYYYMMDD format
        start_yyyymmdd = date_from.replace("-", "")
        end_yyyymmdd = date_to.replace("-", "")
        nasa_resp = await client.get(
            NASA_POWER_URL,
            params={
                "parameters": "GWETROOT",
                "community": "AG",
                "longitude": longitude,
                "latitude": latitude,
                "start": start_yyyymmdd,
                "end": end_yyyymmdd,
                "format": "JSON",
            },
        )
        nasa_resp.raise_for_status()
        nasa_data = nasa_resp.json()

    # Parse Open-Meteo
    daily = meteo_data.get("daily", {})
    temps = [t for t in (daily.get("temperature_2m_mean") or []) if t is not None]
    precips = [p for p in (daily.get("precipitation_sum") or []) if p is not None]
    et0s = [e for e in (daily.get("et0_fao_evapotranspiration") or []) if e is not None]

    avg_temp = sum(temps) / len(temps) if temps else 25.0
    total_precip = sum(precips) if precips else 500.0
    avg_et0 = sum(et0s) / len(et0s) if et0s else 5.0

    # Parse NASA POWER (GWETROOT = root zone soil wetness, 0-1)
    gwetroot_values = nasa_data.get("properties", {}).get("parameter", {}).get("GWETROOT", {})
    moisture_values = [v for v in gwetroot_values.values() if v is not None and v > -990]
    soil_moisture = sum(moisture_values) / len(moisture_values) if moisture_values else 0.4

    result = {
        "avg_temperature": round(avg_temp, 2),
        "total_precipitation": round(total_precip, 2),
        "et0": round(avg_et0, 2),
        "soil_moisture": round(soil_moisture, 4),
        "date_from": date_from,
        "date_to": date_to,
        "meteo_days": len(temps),
        "nasa_days": len(moisture_values),
    }

    logger.info(
        "Climate data for (%.4f, %.4f): temp=%.1f°C, precip=%.0fmm, ET0=%.1f, moisture=%.3f",
        latitude, longitude, avg_temp, total_precip, avg_et0, soil_moisture,
    )

    return result
