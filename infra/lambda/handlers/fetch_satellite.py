"""Lambda handler: Step 2 — Sentinel Hub NDVI fetch."""

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app_pkg"))

from shared.db import get_application, get_conn, get_parcela, insert_satellite_data

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    application_id = event["application_id"]
    logger.info("fetch-satellite: %s", application_id)

    conn = get_conn()
    try:
        app = get_application(conn, application_id)
        if not app:
            raise Exception(f"Application {application_id} not found")

        parcela = get_parcela(conn, app["parcela_id"])

        from app.pipeline.satellite import fetch_ndvi

        data = asyncio.run(
            fetch_ndvi(
                latitude=parcela["latitude"],
                longitude=parcela["longitude"],
            )
        )

        insert_satellite_data(conn, app["id"], data["ndvi_mean"], data)

        return {
            "application_id": application_id,
            "status": "completed",
            "ndvi_mean": data["ndvi_mean"],
        }
    finally:
        conn.close()
