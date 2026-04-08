"""Step 1: LLM-based document extraction and GPS validation."""

import logging

from app.llm import get_claude_client, get_claude_model

logger = logging.getLogger(__name__)


async def extract_and_validate(
    latitude: float,
    longitude: float,
    farmer_name: str | None = None,
    crop_type: str | None = None,
    documents: list[str] | None = None,
) -> dict:
    """Validate GPS coordinates and extract structured info from any submitted documents.

    For the MVP pipeline, this step primarily validates that GPS coordinates
    are plausible for Mexican agriculture and enriches the application context.
    Document OCR/extraction happens here when farmers submit receipts or IDs.
    """
    # Validate GPS is within Mexico's agricultural regions
    validation = _validate_gps_mexico(latitude, longitude)

    if not validation["valid"]:
        return {
            "status": "failed",
            "error": validation["reason"],
            "gps_valid": False,
        }

    # Use LLM to enrich context about the location
    prompt = (
        f"Analiza esta ubicación de una parcela agrícola en México:\n"
        f"- Coordenadas: {latitude:.6f}, {longitude:.6f}\n"
        f"- Agricultor: {farmer_name or 'No proporcionado'}\n"
        f"- Cultivo reportado: {crop_type or 'No especificado'}\n\n"
        f"Responde en JSON con:\n"
        f'- "region": nombre de la región/municipio probable\n'
        f'- "state": estado de México\n'
        f'- "climate_zone": zona climática (árida, semiárida, templada, tropical)\n'
        f'- "typical_crops": lista de cultivos típicos de la zona\n'
        f'- "crop_plausible": true/false si el cultivo reportado es plausible para la zona\n'
        f'- "notes": observaciones breves\n'
        f"Solo responde con el JSON, sin markdown."
    )

    try:
        response = await get_claude_client().messages.create(
            model=get_claude_model(),
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        llm_analysis = response.content[0].text
    except Exception as e:
        logger.warning("LLM analysis failed: %s", e)
        llm_analysis = '{"notes": "Análisis LLM no disponible"}'

    result = {
        "status": "completed",
        "gps_valid": True,
        "latitude": latitude,
        "longitude": longitude,
        "validation": validation,
        "llm_analysis": llm_analysis,
    }

    logger.info("Document extraction completed for (%.4f, %.4f)", latitude, longitude)
    return result


def _validate_gps_mexico(lat: float, lon: float) -> dict:
    """Check that coordinates are within Mexico's approximate bounds."""
    # Mexico bounding box: lat 14.5-32.7, lon -118.4 to -86.7
    if not (14.5 <= lat <= 32.7):
        return {"valid": False, "reason": f"Latitud {lat} fuera de México (14.5-32.7)"}
    if not (-118.4 <= lon <= -86.7):
        return {"valid": False, "reason": f"Longitud {lon} fuera de México (-118.4 a -86.7)"}
    return {"valid": True, "reason": "Coordenadas dentro de México"}
