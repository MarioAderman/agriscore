"""Step 5: Generate farmer expediente (report) and notify via WhatsApp."""

import logging

from app.services import evolution

logger = logging.getLogger(__name__)


async def generate_and_notify(
    phone: str,
    farmer_name: str | None,
    total_score: float,
    sub_productive: float,
    sub_climate: float,
    sub_behavioral: float,
    sub_esg: float,
) -> dict:
    """Generate the expediente summary and notify the farmer via WhatsApp."""

    # Determine risk category
    if total_score >= 65:
        category = "Bajo Riesgo"
        emoji = "🟢"
    elif total_score >= 40:
        category = "Riesgo Moderado"
        emoji = "🟡"
    else:
        category = "Riesgo Alto"
        emoji = "🔴"

    name = farmer_name or "Agricultor"

    message = (
        f"🌾 *Resultado AgriScore* 🌾\n\n"
        f"Hola {name}, tu evaluación está lista:\n\n"
        f"*AgriScore: {total_score:.0f}/100* {emoji}\n"
        f"Categoría: {category}\n\n"
        f"📊 *Desglose:*\n"
        f"  🌱 Productivo: {sub_productive:.0f}/100\n"
        f"  🌤️ Climático: {sub_climate:.0f}/100\n"
        f"  ⭐ Comportamiento: {sub_behavioral:.0f}/100\n"
        f"  ♻️ ESG: {sub_esg:.0f}/100\n\n"
        f"Este perfil ya está disponible para que cualquier institución financiera lo consulte. "
        f"¡Completa retos mensuales para mejorar tu puntaje!"
    )

    # Send via WhatsApp
    try:
        await evolution.send_text(phone, message)
        logger.info("Expediente notification sent to %s", phone)
    except Exception as e:
        logger.warning("Failed to send notification to %s: %s", phone, e)

    return {
        "status": "completed",
        "notification_sent": True,
        "category": category,
        "message_preview": message[:100],
    }
