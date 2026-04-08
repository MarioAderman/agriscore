"""Internal endpoints called by Step Functions (via Lambda proxy) to execute pipeline steps."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.database import (
    AgriScoreResult,
    Application,
    ApplicationStatus,
    ClimateData,
    Farmer,
    Parcela,
    SatelliteData,
    SocioeconomicData,
)
from app.pipeline import climate, document, expediente, satellite, scoring, socioeconomic

router = APIRouter()
logger = logging.getLogger(__name__)


async def _get_application(application_id: str, db: AsyncSession) -> Application | None:
    result = await db.execute(select(Application).where(Application.id == application_id))
    return result.scalar_one_or_none()


async def _get_parcela(parcela_id, db: AsyncSession) -> Parcela | None:
    result = await db.execute(select(Parcela).where(Parcela.id == parcela_id))
    return result.scalar_one_or_none()


@router.post("/extract-docs/{application_id}")
async def extract_docs(application_id: str, db: AsyncSession = Depends(get_db)):
    """Step 1: LLM document extraction + GPS validation."""
    logger.info("Pipeline step 1: extract-docs for %s", application_id)

    app = await _get_application(application_id, db)
    if not app:
        return {"status": "error", "detail": "Application not found"}

    parcela = await _get_parcela(app.parcela_id, db)
    if not parcela or not parcela.latitude:
        return {"status": "error", "detail": "No GPS coordinates"}

    # Get farmer info for enrichment
    result = await db.execute(select(Farmer).where(Farmer.id == app.farmer_id))
    farmer = result.scalar_one_or_none()

    data = await document.extract_and_validate(
        latitude=parcela.latitude,
        longitude=parcela.longitude,
        farmer_name=farmer.name if farmer else None,
        crop_type=parcela.crop_type,
    )

    return {
        "application_id": application_id,
        "step": "extract-docs",
        "status": data["status"],
        "gps_valid": data["gps_valid"],
        "latitude": parcela.latitude,
        "longitude": parcela.longitude,
    }


@router.post("/fetch-satellite/{application_id}")
async def fetch_satellite(application_id: str, db: AsyncSession = Depends(get_db)):
    """Step 2: Sentinel Hub NDVI fetch."""
    logger.info("Pipeline step 2: fetch-satellite for %s", application_id)

    app = await _get_application(application_id, db)
    if not app:
        return {"status": "error", "detail": "Application not found"}

    parcela = await _get_parcela(app.parcela_id, db)

    data = await satellite.fetch_ndvi(
        latitude=parcela.latitude,
        longitude=parcela.longitude,
    )

    # Store results
    sat = SatelliteData(
        application_id=app.id,
        ndvi_mean=data["ndvi_mean"],
        raw_data=data,
    )
    db.add(sat)
    await db.commit()

    return {
        "application_id": application_id,
        "step": "fetch-satellite",
        "status": "completed",
        "ndvi_mean": data["ndvi_mean"],
    }


@router.post("/fetch-climate/{application_id}")
async def fetch_climate(application_id: str, db: AsyncSession = Depends(get_db)):
    """Step 3a: Open-Meteo + NASA POWER climate data."""
    logger.info("Pipeline step 3a: fetch-climate for %s", application_id)

    app = await _get_application(application_id, db)
    if not app:
        return {"status": "error", "detail": "Application not found"}

    parcela = await _get_parcela(app.parcela_id, db)

    data = await climate.fetch_climate_data(
        latitude=parcela.latitude,
        longitude=parcela.longitude,
    )

    # Store results
    clim = ClimateData(
        application_id=app.id,
        avg_temperature=data["avg_temperature"],
        total_precipitation=data["total_precipitation"],
        et0=data["et0"],
        soil_moisture=data["soil_moisture"],
        raw_data=data,
    )
    db.add(clim)
    await db.commit()

    return {
        "application_id": application_id,
        "step": "fetch-climate",
        "status": "completed",
        "avg_temperature": data["avg_temperature"],
        "total_precipitation": data["total_precipitation"],
    }


@router.post("/fetch-socioeconomic/{application_id}")
async def fetch_socioeconomic(application_id: str, db: AsyncSession = Depends(get_db)):
    """Step 3b: INEGI Indicadores + DENUE."""
    logger.info("Pipeline step 3b: fetch-socioeconomic for %s", application_id)

    app = await _get_application(application_id, db)
    if not app:
        return {"status": "error", "detail": "Application not found"}

    parcela = await _get_parcela(app.parcela_id, db)

    data = await socioeconomic.fetch_socioeconomic_data(
        latitude=parcela.latitude,
        longitude=parcela.longitude,
    )

    # Store results
    socio = SocioeconomicData(
        application_id=app.id,
        population=data["population"],
        agri_establishments=data["agri_establishments"],
        raw_data=data,
    )
    db.add(socio)
    await db.commit()

    return {
        "application_id": application_id,
        "step": "fetch-socioeconomic",
        "status": "completed",
        "agri_establishments": data["agri_establishments"],
    }


@router.post("/calculate-score/{application_id}")
async def calculate_score(
    application_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Step 4: ML model prediction + sub-scores."""
    logger.info("Pipeline step 4: calculate-score for %s", application_id)

    app = await _get_application(application_id, db)
    if not app:
        return {"status": "error", "detail": "Application not found"}

    parcela = await _get_parcela(app.parcela_id, db)

    # Load pipeline data from DB
    sat_result = await db.execute(select(SatelliteData).where(SatelliteData.application_id == app.id))
    sat = sat_result.scalar_one_or_none()

    clim_result = await db.execute(select(ClimateData).where(ClimateData.application_id == app.id))
    clim = clim_result.scalar_one_or_none()

    socio_result = await db.execute(select(SocioeconomicData).where(SocioeconomicData.application_id == app.id))
    socio = socio_result.scalar_one_or_none()

    if not sat or not clim:
        return {"status": "error", "detail": "Missing satellite or climate data"}

    # Get ML model from app state
    model = request.app.state.ml_model
    if not model:
        return {"status": "error", "detail": "ML model not loaded"}

    scores = scoring.predict_agriscore(
        model=model,
        ndvi_mean=sat.ndvi_mean,
        ndvi_trend=0.02,  # Default trend for first evaluation
        avg_temperature=clim.avg_temperature,
        total_precipitation=clim.total_precipitation,
        soil_moisture=clim.soil_moisture,
        et0=clim.et0,
        area_hectares=parcela.area_hectares or 5.0,
        crop_type=parcela.crop_type,
        agri_establishments=socio.agri_establishments if socio else 100,
        months_active=1,
        challenges_completed=0,
    )

    # Store result
    agriscore = AgriScoreResult(
        application_id=app.id,
        total_score=scores["total_score"],
        sub_productive=scores["sub_productive"],
        sub_climate=scores["sub_climate"],
        sub_behavioral=scores["sub_behavioral"],
        sub_esg=scores["sub_esg"],
    )
    db.add(agriscore)
    await db.commit()

    return {
        "application_id": application_id,
        "step": "calculate-score",
        "status": "completed",
        **scores,
    }


@router.post("/generate-expediente/{application_id}")
async def generate_expediente(application_id: str, db: AsyncSession = Depends(get_db)):
    """Step 5: Generate report, store in RDS, notify farmer."""
    logger.info("Pipeline step 5: generate-expediente for %s", application_id)

    app = await _get_application(application_id, db)
    if not app:
        return {"status": "error", "detail": "Application not found"}

    # Get farmer and score
    farmer_result = await db.execute(select(Farmer).where(Farmer.id == app.farmer_id))
    farmer = farmer_result.scalar_one_or_none()

    score_result = await db.execute(select(AgriScoreResult).where(AgriScoreResult.application_id == app.id))
    score = score_result.scalar_one_or_none()

    if not score:
        return {"status": "error", "detail": "No score calculated"}

    # Mark application as completed
    app.status = ApplicationStatus.completed
    app.completed_at = datetime.now(timezone.utc)
    await db.commit()

    # Notify farmer
    result = await expediente.generate_and_notify(
        phone=farmer.phone,
        farmer_name=farmer.name,
        total_score=score.total_score,
        sub_productive=score.sub_productive,
        sub_climate=score.sub_climate,
        sub_behavioral=score.sub_behavioral,
        sub_esg=score.sub_esg,
    )

    return {
        "application_id": application_id,
        "step": "generate-expediente",
        **result,
    }
