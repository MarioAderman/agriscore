"""Lambda handler: Step 3b — INEGI socioeconomic data."""

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app_pkg"))

from shared.db import get_application, get_conn, get_parcela, insert_socioeconomic_data

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    application_id = event["application_id"]
    logger.info("fetch-socioeconomic: %s", application_id)

    conn = get_conn()
    try:
        app = get_application(conn, application_id)
        if not app:
            raise Exception(f"Application {application_id} not found")

        parcela = get_parcela(conn, app["parcela_id"])

        from app.pipeline.socioeconomic import fetch_socioeconomic_data

        data = asyncio.run(
            fetch_socioeconomic_data(
                latitude=parcela["latitude"],
                longitude=parcela["longitude"],
            )
        )

        insert_socioeconomic_data(
            conn,
            app["id"],
            data["population"],
            data["agri_establishments"],
            data,
        )

        return {
            "application_id": application_id,
            "status": "completed",
            "agri_establishments": data["agri_establishments"],
        }
    finally:
        conn.close()
