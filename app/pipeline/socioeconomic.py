"""Step 3b: Fetch socioeconomic data from INEGI (Indicadores + DENUE)."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

INEGI_INDICADORES_URL = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR"
INEGI_DENUE_URL = "https://www.inegi.org.mx/app/api/denue/v1/consulta/buscar"

# Indicator IDs
POPULATION_INDICATOR = "1002000001"  # Total population

# Approximate lat/lon bounding boxes for Mexican states
# Format: state_code -> (lat_min, lat_max, lon_min, lon_max)
_STATE_BOUNDS = {
    "01": (21.6, 22.9, -103.1, -101.8),  # Aguascalientes
    "02": (28.0, 32.7, -117.3, -112.8),  # Baja California
    "03": (22.9, 28.0, -115.1, -109.4),  # Baja California Sur
    "04": (17.8, 19.5, -92.5, -89.1),  # Campeche
    "05": (24.5, 29.9, -103.8, -99.8),  # Coahuila
    "06": (18.7, 19.6, -104.7, -103.5),  # Colima
    "07": (14.5, 17.6, -94.2, -90.4),  # Chiapas
    "08": (26.3, 31.8, -109.1, -103.3),  # Chihuahua
    "09": (19.1, 19.6, -99.4, -98.9),  # CDMX
    "10": (22.3, 26.9, -107.2, -103.4),  # Durango
    "11": (20.0, 21.8, -102.1, -99.6),  # Guanajuato
    "12": (16.3, 18.9, -102.2, -98.0),  # Guerrero
    "13": (19.6, 21.4, -99.9, -97.9),  # Hidalgo
    "14": (19.1, 22.8, -105.7, -101.5),  # Jalisco
    "15": (18.3, 20.3, -100.6, -98.6),  # Estado de México
    "16": (17.9, 20.4, -103.7, -100.1),  # Michoacán
    "17": (18.3, 19.3, -99.5, -98.6),  # Morelos
    "18": (20.6, 23.1, -105.8, -103.7),  # Nayarit
    "19": (23.1, 27.8, -101.2, -98.4),  # Nuevo León
    "20": (15.6, 18.7, -98.1, -95.4),  # Oaxaca
    "21": (18.0, 20.8, -98.9, -96.7),  # Puebla
    "22": (20.0, 21.7, -100.6, -99.0),  # Querétaro
    "23": (18.5, 21.6, -88.3, -86.7),  # Quintana Roo
    "24": (21.1, 24.5, -102.3, -98.3),  # San Luis Potosí
    "25": (22.5, 27.1, -109.5, -105.3),  # Sinaloa
    "26": (26.3, 33.0, -114.8, -108.6),  # Sonora
    "27": (17.2, 18.7, -94.1, -91.0),  # Tabasco
    "28": (22.2, 27.7, -100.2, -97.1),  # Tamaulipas
    "29": (19.1, 19.8, -98.7, -97.6),  # Tlaxcala
    "30": (17.1, 22.5, -98.7, -93.6),  # Veracruz
    "31": (19.5, 21.7, -91.1, -87.4),  # Yucatán
    "32": (21.0, 25.1, -104.4, -101.8),  # Zacatecas
}


def _coords_to_state(lat: float, lon: float) -> str:
    """Best-effort lat/lon → INEGI state code. Falls back to '00' (national)."""
    best = None
    best_dist = float("inf")
    for code, (lat_min, lat_max, lon_min, lon_max) in _STATE_BOUNDS.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return code
        # Track closest as fallback
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2
        dist = (lat - center_lat) ** 2 + (lon - center_lon) ** 2
        if dist < best_dist:
            best_dist = dist
            best = code
    return best or "00"


async def fetch_socioeconomic_data(
    latitude: float,
    longitude: float,
    state_code: str | None = None,
) -> dict:
    """Fetch socioeconomic data: population from INEGI Indicadores,
    agricultural establishments from DENUE.

    Returns dict with population, agri_establishments, and raw data.
    Falls back to defaults if INEGI is unreachable.
    """
    if not state_code:
        state_code = _coords_to_state(latitude, longitude)
    logger.info("Socioeconomic: state_code=%s for (%.4f, %.4f)", state_code, latitude, longitude)

    token = settings.inegi_token
    population = None
    agri_establishments = 0

    async with httpx.AsyncClient(timeout=30) as client:
        # INEGI Indicadores: population for the state
        try:
            pop_resp = await client.get(
                f"{INEGI_INDICADORES_URL}/{POPULATION_INDICATOR}/es/{state_code}/true/bib/2.0/{token}",
                params={"type": "json"},
            )
            pop_resp.raise_for_status()
            pop_data = pop_resp.json()

            series = pop_data.get("Series", [{}])
            if series:
                observations = series[0].get("OBSERVATIONS", [])
                if observations:
                    population = int(float(observations[-1].get("OBS_VALUE", 0)))
        except Exception as e:
            logger.warning("INEGI Indicadores failed: %s", e)

        # INEGI DENUE: agricultural establishments near the location
        try:
            denue_resp = await client.get(
                f"{INEGI_DENUE_URL}/agricultura/{latitude},{longitude}/5000/{token}",
            )
            denue_resp.raise_for_status()
            denue_data = denue_resp.json()
            if isinstance(denue_data, list):
                agri_establishments = len(denue_data)
        except Exception as e:
            logger.warning("INEGI DENUE failed: %s", e)

    result = {
        "population": population,
        "agri_establishments": agri_establishments,
        "state_code": state_code,
        "search_radius_m": 5000,
    }

    logger.info(
        "Socioeconomic data for (%.4f, %.4f): population=%s, agri_establishments=%d",
        latitude,
        longitude,
        population,
        agri_establishments,
    )

    return result
