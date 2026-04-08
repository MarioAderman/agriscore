"""Lambda handler: Step 4 — ML model prediction + sub-scores."""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app_pkg"))

from shared.db import (
    get_application,
    get_climate_data,
    get_conn,
    get_parcela,
    get_satellite_data,
    get_socioeconomic_data,
    insert_agriscore_result,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Module-level model cache — survives across warm Lambda invocations
_model = None


def _load_model():
    """Load ML model from S3 (or local file for testing), cache for warm reuse."""
    global _model
    if _model is not None:
        return _model

    import joblib

    # Local model path (for testing outside Lambda)
    local_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "model.pkl")
    if os.path.exists(local_path):
        _model = joblib.load(local_path)
        logger.info("ML model loaded from local file")
        return _model

    # Lambda: download from S3 to /tmp
    import boto3

    model_path = "/tmp/model.pkl"
    if not os.path.exists(model_path):
        s3 = boto3.client("s3")
        bucket = os.environ.get("S3_BUCKET", "agriscore-data")
        logger.info("Downloading model from s3://%s/ml/model.pkl", bucket)
        s3.download_file(bucket, "ml/model.pkl", model_path)

    _model = joblib.load(model_path)
    logger.info("ML model loaded from S3")
    return _model


def handler(event, context):
    application_id = event["application_id"]
    logger.info("calculate-score: %s", application_id)

    conn = get_conn()
    try:
        app = get_application(conn, application_id)
        if not app:
            raise Exception(f"Application {application_id} not found")

        parcela = get_parcela(conn, app["parcela_id"])
        sat = get_satellite_data(conn, app["id"])
        clim = get_climate_data(conn, app["id"])
        socio = get_socioeconomic_data(conn, app["id"])

        if not sat or not clim:
            raise Exception("Missing satellite or climate data")

        model = _load_model()

        from app.pipeline.scoring import predict_agriscore

        scores = predict_agriscore(
            model=model,
            ndvi_mean=sat["ndvi_mean"],
            ndvi_trend=0.02,
            avg_temperature=clim["avg_temperature"],
            total_precipitation=clim["total_precipitation"],
            soil_moisture=clim["soil_moisture"],
            et0=clim["et0"],
            area_hectares=parcela["area_hectares"] or 5.0,
            crop_type=parcela["crop_type"],
            agri_establishments=socio["agri_establishments"] if socio else 100,
            months_active=1,
            challenges_completed=0,
        )

        insert_agriscore_result(
            conn,
            app["id"],
            scores["total_score"],
            scores["sub_productive"],
            scores["sub_climate"],
            scores["sub_behavioral"],
            scores["sub_esg"],
        )

        return {
            "application_id": application_id,
            "status": "completed",
            **scores,
        }
    finally:
        conn.close()
