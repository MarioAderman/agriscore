"""Lambda handler: Step 5 — Generate expediente, notify farmer via WhatsApp.

WhatsApp call is inlined here to avoid importing app.services.evolution
(which triggers the full app.config.settings import chain).
"""

import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.db import get_agriscore_result, get_application, get_conn, get_farmer, mark_application_completed

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _send_whatsapp(phone: str, text: str):
    """Send a WhatsApp message via EvolutionAPI (sync, no extra deps)."""
    base_url = os.environ.get("EVOLUTIONAPI_URL", "http://localhost:8080")
    instance = os.environ.get("EVOLUTION_INSTANCE_NAME", "Fintegra solutions")
    api_key = os.environ.get("EVOLUTIONAPI_AUTHENTICATION_API_KEY", "")

    url = f"{base_url}/message/sendText/{urllib.parse.quote(instance)}"
    data = json.dumps({"number": phone, "text": text}).encode()

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "apikey": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        logger.warning("WhatsApp notification failed: %s", e)
        return {}


def handler(event, context):
    application_id = event["application_id"]
    logger.info("generate-expediente: %s", application_id)

    conn = get_conn()
    try:
        app = get_application(conn, application_id)
        if not app:
            raise Exception(f"Application {application_id} not found")

        farmer = get_farmer(conn, app["farmer_id"])
        score = get_agriscore_result(conn, app["id"])

        if not score:
            raise Exception("No score calculated")

        # Mark completed
        mark_application_completed(conn, application_id)

        # Build notification message
        total = score["total_score"]
        if total >= 65:
            category, emoji = "Bajo Riesgo", "\U0001f7e2"
        elif total >= 40:
            category, emoji = "Riesgo Moderado", "\U0001f7e1"
        else:
            category, emoji = "Riesgo Alto", "\U0001f534"

        name = farmer["name"] if farmer else "Agricultor"

        message = (
            f"\U0001f33e *Resultado AgriScore* \U0001f33e\n\n"
            f"Hola {name}, tu evaluaci\u00f3n est\u00e1 lista:\n\n"
            f"*AgriScore: {total:.0f}/100* {emoji}\n"
            f"Categor\u00eda: {category}\n\n"
            f"\U0001f4ca *Desglose:*\n"
            f"  \U0001f331 Productivo: {score['sub_productive']:.0f}/100\n"
            f"  \U0001f324\ufe0f Clim\u00e1tico: {score['sub_climate']:.0f}/100\n"
            f"  \u2b50 Comportamiento: {score['sub_behavioral']:.0f}/100\n"
            f"  \u267b\ufe0f ESG: {score['sub_esg']:.0f}/100\n\n"
            f"Este perfil ya est\u00e1 disponible para que cualquier instituci\u00f3n financiera lo consulte. "
            f"\u00a1Completa retos mensuales para mejorar tu puntaje!"
        )

        # Send WhatsApp notification
        if farmer and farmer.get("phone"):
            _send_whatsapp(farmer["phone"], message)
            logger.info("Notification sent to %s", farmer["phone"])

        return {
            "application_id": application_id,
            "status": "completed",
            "category": category,
            "notification_sent": True,
        }
    finally:
        conn.close()
