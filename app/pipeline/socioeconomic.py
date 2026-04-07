"""Step 3b: Fetch socioeconomic data from INEGI (Indicadores + DENUE)."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

INEGI_INDICADORES_URL = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR"
INEGI_DENUE_URL = "https://www.inegi.org.mx/app/api/denue/v1/consulta/buscar"

# Indicator IDs
POPULATION_INDICATOR = "1002000001"  # Total population


async def fetch_socioeconomic_data(
    latitude: float,
    longitude: float,
    state_code: str = "25",  # Default: Sinaloa
) -> dict:
    """Fetch socioeconomic data: population from INEGI Indicadores,
    agricultural establishments from DENUE.

    Returns dict with population, agri_establishments, and raw data.
    """
    token = settings.inegi_token

    async with httpx.AsyncClient(timeout=30) as client:
        # INEGI Indicadores: population for the state
        pop_resp = await client.get(
            f"{INEGI_INDICADORES_URL}/{POPULATION_INDICATOR}/es/{state_code}/true/bib/2.0/{token}",
            params={"type": "json"},
        )
        pop_resp.raise_for_status()
        pop_data = pop_resp.json()

        # INEGI DENUE: agricultural establishments near the location
        # Search: "agricultura" within 5km radius
        denue_resp = await client.get(
            f"{INEGI_DENUE_URL}/agricultura/{latitude},{longitude}/5000/{token}",
        )
        denue_resp.raise_for_status()
        denue_data = denue_resp.json()

    # Parse population (get most recent value)
    population = None
    try:
        series = pop_data.get("Series", [{}])
        if series:
            observations = series[0].get("OBSERVATIONS", [])
            if observations:
                # Get last observation (most recent)
                population = int(float(observations[-1].get("OBS_VALUE", 0)))
    except (KeyError, IndexError, ValueError) as e:
        logger.warning("Failed to parse population: %s", e)

    # Parse DENUE establishments count
    agri_establishments = 0
    if isinstance(denue_data, list):
        agri_establishments = len(denue_data)

    result = {
        "population": population,
        "agri_establishments": agri_establishments,
        "state_code": state_code,
        "search_radius_m": 5000,
    }

    logger.info(
        "Socioeconomic data for (%.4f, %.4f): population=%s, agri_establishments=%d",
        latitude, longitude, population, agri_establishments,
    )

    return result
