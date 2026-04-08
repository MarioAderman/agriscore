"""Pipeline orchestrator — triggers Step Functions or runs locally."""

import asyncio
import logging
from datetime import datetime, timezone

import joblib

from app.config import settings
from app.db.connection import async_session
from app.models.database import (
    AgriScoreResult,
    Application,
    ApplicationStatus,
    ClimateData,
    SatelliteData,
    SocioeconomicData,
)
from app.pipeline import climate, document, expediente, satellite, socioeconomic
from app.pipeline.scoring import predict_agriscore

logger = logging.getLogger(__name__)

# Module-level model cache
_model = None


def _load_model():
    """Load ML model from disk, cache for reuse."""
    global _model
    if _model is not None:
        return _model
    _model = joblib.load("ml/model.pkl")
    logger.info("ML model loaded from ml/model.pkl")
    return _model


async def run_pipeline_local(application_id: str, base_url: str = "http://localhost:8000"):
    """Run all 5 pipeline steps locally via direct function calls.

    Used for local development and as a fallback if Step Functions is not configured.
    """
    async with async_session() as db:
        # Load application + related objects
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        result = await db.execute(
            select(Application)
            .options(selectinload(Application.parcela), selectinload(Application.farmer))
            .where(Application.id == application_id)
        )
        app = result.scalar_one_or_none()
        if not app:
            logger.error("Application %s not found", application_id)
            return {"status": "error", "error": f"Application {application_id} not found"}

        parcela = app.parcela
        farmer = app.farmer
        lat = parcela.latitude
        lon = parcela.longitude

        app.status = ApplicationStatus.processing
        await db.commit()

        # Step 1: Extract docs / validate GPS
        logger.info("Pipeline [%s]: Step 1 — Extract docs", application_id)
        try:
            step1 = await document.extract_and_validate(
                lat, lon, farmer_name=farmer.name, crop_type=parcela.crop_type
            )
            if step1.get("status") == "failed":
                app.status = ApplicationStatus.failed
                await db.commit()
                logger.error("Step 1 failed: %s", step1)
                return step1
        except Exception as e:
            logger.error("Step 1 exception: %s", e)
            app.status = ApplicationStatus.failed
            await db.commit()
            return {"status": "error", "error": str(e)}

        # Steps 2, 3a, 3b in parallel
        logger.info("Pipeline [%s]: Steps 2+3 — Parallel fetch", application_id)
        try:
            sat_result, clim_result, socio_result = await asyncio.gather(
                satellite.fetch_ndvi(lat, lon),
                climate.fetch_climate_data(lat, lon),
                socioeconomic.fetch_socioeconomic_data(lat, lon),
            )
        except Exception as e:
            logger.error("Parallel fetch failed: %s", e)
            app.status = ApplicationStatus.failed
            await db.commit()
            return {"status": "error", "error": str(e)}

        # Save fetched data to DB
        sat_record = SatelliteData(
            application_id=app.id,
            ndvi_mean=sat_result["ndvi_mean"],
            raw_data=sat_result,
        )
        clim_record = ClimateData(
            application_id=app.id,
            avg_temperature=clim_result["avg_temperature"],
            total_precipitation=clim_result["total_precipitation"],
            et0=clim_result["et0"],
            soil_moisture=clim_result["soil_moisture"],
            raw_data=clim_result,
        )
        socio_record = SocioeconomicData(
            application_id=app.id,
            population=socio_result.get("population"),
            agri_establishments=socio_result.get("agri_establishments", 0),
            raw_data=socio_result,
        )
        db.add_all([sat_record, clim_record, socio_record])
        await db.commit()

        # Step 4: Calculate score
        logger.info("Pipeline [%s]: Step 4 — Calculate score", application_id)
        try:
            model = _load_model()
            scores = predict_agriscore(
                model=model,
                ndvi_mean=sat_result["ndvi_mean"],
                ndvi_trend=0.02,
                avg_temperature=clim_result["avg_temperature"],
                total_precipitation=clim_result["total_precipitation"],
                soil_moisture=clim_result["soil_moisture"],
                et0=clim_result["et0"],
                area_hectares=parcela.area_hectares or 5.0,
                crop_type=parcela.crop_type,
                agri_establishments=socio_result.get("agri_establishments", 100),
                months_active=1,
                challenges_completed=0,
            )
        except Exception as e:
            logger.error("Scoring failed: %s", e)
            app.status = ApplicationStatus.failed
            await db.commit()
            return {"status": "error", "error": str(e)}

        # Save AgriScore result
        score_record = AgriScoreResult(
            application_id=app.id,
            total_score=scores["total_score"],
            sub_productive=scores["sub_productive"],
            sub_climate=scores["sub_climate"],
            sub_behavioral=scores["sub_behavioral"],
            sub_esg=scores["sub_esg"],
        )
        db.add(score_record)
        app.status = ApplicationStatus.completed
        app.completed_at = datetime.now(timezone.utc)
        await db.commit()

        # Step 5: Generate expediente + notify
        logger.info("Pipeline [%s]: Step 5 — Generate expediente", application_id)
        try:
            await expediente.generate_and_notify(
                phone=farmer.phone,
                farmer_name=farmer.name,
                total_score=scores["total_score"],
                sub_productive=scores["sub_productive"],
                sub_climate=scores["sub_climate"],
                sub_behavioral=scores["sub_behavioral"],
                sub_esg=scores["sub_esg"],
            )
        except Exception as e:
            logger.warning("Expediente notification failed (non-fatal): %s", e)

        logger.info(
            "Pipeline completed for %s: score=%.0f",
            application_id,
            scores["total_score"],
        )
        return {
            "status": "completed",
            "application_id": str(application_id),
            **scores,
        }


async def trigger_step_functions(application_id: str):
    """Trigger AWS Step Functions execution.

    Falls back to local pipeline if Step Functions ARN is not configured.
    """
    if not settings.step_functions_arn:
        logger.info("Step Functions not configured — running pipeline locally")
        return await run_pipeline_local(application_id)

    import json

    import boto3

    sfn = boto3.client("stepfunctions", region_name=settings.aws_default_region)
    response = sfn.start_execution(
        stateMachineArn=settings.step_functions_arn,
        input=json.dumps({"application_id": str(application_id)}),
    )
    logger.info("Step Functions execution started: %s", response["executionArn"])
    return {"execution_arn": response["executionArn"]}
