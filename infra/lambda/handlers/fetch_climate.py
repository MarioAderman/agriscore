"""Lambda handler: Step 3a — Open-Meteo + NASA POWER climate data."""

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app_pkg"))

from shared.db import get_application, get_conn, get_parcela, insert_climate_data

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    application_id = event["application_id"]
    logger.info("fetch-climate: %s", application_id)

    conn = get_conn()
    try:
        app = get_application(conn, application_id)
        if not app:
            raise Exception(f"Application {application_id} not found")

        parcela = get_parcela(conn, app["parcela_id"])

        from app.pipeline.climate import fetch_climate_data

        data = asyncio.run(
            fetch_climate_data(
                latitude=parcela["latitude"],
                longitude=parcela["longitude"],
            )
        )

        insert_climate_data(
            conn,
            app["id"],
            data["avg_temperature"],
            data["total_precipitation"],
            data["et0"],
            data["soil_moisture"],
            data,
        )

        return {
            "application_id": application_id,
            "status": "completed",
            "avg_temperature": data["avg_temperature"],
            "total_precipitation": data["total_precipitation"],
        }
    finally:
        conn.close()
