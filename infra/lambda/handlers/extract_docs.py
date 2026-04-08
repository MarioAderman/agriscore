"""Lambda handler: Step 1 — LLM document extraction + GPS validation."""

import asyncio
import logging
import os
import sys

# Add parent dirs so shared and app packages are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app_pkg"))

from shared.db import get_application, get_conn, get_farmer, get_parcela

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    application_id = event["application_id"]
    logger.info("extract-docs: %s", application_id)

    conn = get_conn()
    try:
        app = get_application(conn, application_id)
        if not app:
            raise Exception(f"Application {application_id} not found")

        parcela = get_parcela(conn, app["parcela_id"])
        if not parcela or not parcela["latitude"]:
            raise Exception("No GPS coordinates")

        farmer = get_farmer(conn, app["farmer_id"])

        # Import pipeline module (uses app.config.settings from env vars)
        from app.pipeline.document import extract_and_validate

        data = asyncio.run(
            extract_and_validate(
                latitude=parcela["latitude"],
                longitude=parcela["longitude"],
                farmer_name=farmer["name"] if farmer else None,
                crop_type=parcela["crop_type"],
            )
        )

        if data["status"] == "error":
            raise Exception(f"Extract failed: {data.get('error', 'unknown')}")

        return {
            "application_id": application_id,
            "status": data["status"],
            "gps_valid": data["gps_valid"],
            "latitude": parcela["latitude"],
            "longitude": parcela["longitude"],
        }
    finally:
        conn.close()
