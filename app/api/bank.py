"""Bank API — endpoints consumed by financial institutions to view farmer profiles and scores."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, verify_bank_api_key
from app.models.database import (
    AgriScoreResult,
    Application,
    ApplicationStatus,
    Challenge,
    ChallengeStatus,
    ClimateData,
    Farmer,
    Parcela,
    SatelliteData,
    SocioeconomicData,
)

router = APIRouter(dependencies=[Depends(verify_bank_api_key)])


@router.get("/farmers")
async def list_farmers(db: AsyncSession = Depends(get_db)):
    """List all farmers that have a completed AgriScore."""
    result = await db.execute(
        select(
            Farmer.id,
            Farmer.name,
            Farmer.phone,
            Farmer.created_at,
            Parcela.crop_type,
            Parcela.latitude,
            Parcela.longitude,
            AgriScoreResult.total_score,
            AgriScoreResult.created_at.label("scored_at"),
        )
        .join(Application, Application.farmer_id == Farmer.id)
        .join(AgriScoreResult, AgriScoreResult.application_id == Application.id)
        .join(Parcela, Parcela.id == Application.parcela_id)
        .where(Application.status == ApplicationStatus.completed)
        .order_by(AgriScoreResult.total_score.desc())
    )
    rows = result.all()

    return {
        "count": len(rows),
        "farmers": [
            {
                "id": str(r.id),
                "name": r.name,
                "phone": r.phone,
                "crop_type": r.crop_type,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "agriscore": round(r.total_score, 1),
                "scored_at": r.scored_at.isoformat() if r.scored_at else None,
                "registered_at": r.created_at.isoformat(),
            }
            for r in rows
        ],
    }


@router.get("/farmers/{farmer_id}")
async def get_farmer_detail(farmer_id: str, db: AsyncSession = Depends(get_db)):
    """Full farmer profile with latest sub-scores and parcela info."""
    result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=404, detail="Agricultor no encontrado")

    # Parcela
    parcela_result = await db.execute(select(Parcela).where(Parcela.farmer_id == farmer.id))
    parcela = parcela_result.scalar_one_or_none()

    # Latest completed application with score
    score_result = await db.execute(
        select(AgriScoreResult, Application)
        .join(Application, AgriScoreResult.application_id == Application.id)
        .where(Application.farmer_id == farmer.id)
        .order_by(AgriScoreResult.created_at.desc())
        .limit(1)
    )
    score_row = score_result.first()

    # Challenges
    challenge_result = await db.execute(select(Challenge).where(Challenge.farmer_id == farmer.id))
    challenges = challenge_result.scalars().all()

    # Total evaluations
    app_count = await db.execute(
        select(func.count(Application.id))
        .where(Application.farmer_id == farmer.id)
        .where(Application.status == ApplicationStatus.completed)
    )

    response = {
        "id": str(farmer.id),
        "name": farmer.name,
        "phone": farmer.phone,
        "onboarded": farmer.onboarded,
        "registered_at": farmer.created_at.isoformat(),
        "parcela": None,
        "agriscore": None,
        "challenges": {
            "total": len(challenges),
            "completed": sum(1 for c in challenges if c.status == ChallengeStatus.completed),
        },
        "total_evaluations": app_count.scalar() or 0,
    }

    if parcela:
        response["parcela"] = {
            "latitude": parcela.latitude,
            "longitude": parcela.longitude,
            "crop_type": parcela.crop_type,
            "area_hectares": parcela.area_hectares,
        }

    if score_row:
        score, app = score_row
        response["agriscore"] = {
            "total": round(score.total_score, 1),
            "sub_productive": round(score.sub_productive, 1),
            "sub_climate": round(score.sub_climate, 1),
            "sub_behavioral": round(score.sub_behavioral, 1),
            "sub_esg": round(score.sub_esg, 1),
            "scored_at": score.created_at.isoformat(),
            "risk_category": ("bajo" if score.total_score >= 65 else "moderado" if score.total_score >= 40 else "alto"),
        }

    return response


@router.get("/farmers/{farmer_id}/expediente")
async def get_farmer_expediente(farmer_id: str, db: AsyncSession = Depends(get_db)):
    """Full expediente: score + satellite + climate + socioeconomic data."""
    result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=404, detail="Agricultor no encontrado")

    # Latest completed application
    app_result = await db.execute(
        select(Application)
        .where(Application.farmer_id == farmer.id)
        .where(Application.status == ApplicationStatus.completed)
        .order_by(Application.completed_at.desc())
        .limit(1)
    )
    application = app_result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Sin evaluación completada")

    # Load all pipeline data for this application
    score = (
        await db.execute(select(AgriScoreResult).where(AgriScoreResult.application_id == application.id))
    ).scalar_one_or_none()

    sat = (
        await db.execute(select(SatelliteData).where(SatelliteData.application_id == application.id))
    ).scalar_one_or_none()

    clim = (
        await db.execute(select(ClimateData).where(ClimateData.application_id == application.id))
    ).scalar_one_or_none()

    socio = (
        await db.execute(select(SocioeconomicData).where(SocioeconomicData.application_id == application.id))
    ).scalar_one_or_none()

    parcela = (await db.execute(select(Parcela).where(Parcela.id == application.parcela_id))).scalar_one_or_none()

    return {
        "farmer": {
            "id": str(farmer.id),
            "name": farmer.name,
            "phone": farmer.phone,
        },
        "parcela": {
            "latitude": parcela.latitude if parcela else None,
            "longitude": parcela.longitude if parcela else None,
            "crop_type": parcela.crop_type if parcela else None,
            "area_hectares": parcela.area_hectares if parcela else None,
        },
        "agriscore": {
            "total": round(score.total_score, 1),
            "sub_productive": round(score.sub_productive, 1),
            "sub_climate": round(score.sub_climate, 1),
            "sub_behavioral": round(score.sub_behavioral, 1),
            "sub_esg": round(score.sub_esg, 1),
            "scored_at": score.created_at.isoformat(),
        }
        if score
        else None,
        "satellite": {
            "ndvi_mean": sat.ndvi_mean,
            "fetched_at": sat.fetched_at.isoformat(),
            "raw": sat.raw_data,
        }
        if sat
        else None,
        "climate": {
            "avg_temperature": clim.avg_temperature,
            "total_precipitation": clim.total_precipitation,
            "et0": clim.et0,
            "soil_moisture": clim.soil_moisture,
            "fetched_at": clim.fetched_at.isoformat(),
        }
        if clim
        else None,
        "socioeconomic": {
            "population": socio.population,
            "agri_establishments": socio.agri_establishments,
            "fetched_at": socio.fetched_at.isoformat(),
        }
        if socio
        else None,
        "application": {
            "id": str(application.id),
            "status": application.status.value,
            "created_at": application.created_at.isoformat(),
            "completed_at": application.completed_at.isoformat() if application.completed_at else None,
        },
    }


@router.get("/farmers/{farmer_id}/satellite")
async def get_farmer_satellite(
    farmer_id: str,
    type: str = Query("ndvi", pattern="^(ndvi|rgb)$"),
    db: AsyncSession = Depends(get_db),
):
    """Satellite image of a farmer's parcela. type: 'ndvi' or 'rgb'."""
    from app.pipeline.satellite import fetch_image

    result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=404, detail="Agricultor no encontrado")

    parcela = (await db.execute(select(Parcela).where(Parcela.farmer_id == farmer.id))).scalar_one_or_none()
    if not parcela or not parcela.latitude:
        raise HTTPException(status_code=404, detail="Sin ubicación de parcela")

    png_bytes = await fetch_image(
        latitude=parcela.latitude,
        longitude=parcela.longitude,
        image_type=type,
    )
    return Response(content=png_bytes, media_type="image/png")


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Aggregate statistics for bank dashboard."""
    # Total farmers
    total_farmers = (await db.execute(select(func.count(Farmer.id)))).scalar() or 0

    # Farmers with completed scores
    scored_farmers = (
        await db.execute(
            select(func.count(func.distinct(Application.farmer_id))).where(
                Application.status == ApplicationStatus.completed
            )
        )
    ).scalar() or 0

    # Score stats
    score_stats = (
        await db.execute(
            select(
                func.avg(AgriScoreResult.total_score),
                func.min(AgriScoreResult.total_score),
                func.max(AgriScoreResult.total_score),
            )
        )
    ).first()

    avg_score = round(score_stats[0], 1) if score_stats[0] else 0
    min_score = round(score_stats[1], 1) if score_stats[1] else 0
    max_score = round(score_stats[2], 1) if score_stats[2] else 0

    # Risk distribution
    risk_dist = {"bajo": 0, "moderado": 0, "alto": 0}
    scores = (await db.execute(select(AgriScoreResult.total_score))).scalars().all()
    for s in scores:
        if s >= 65:
            risk_dist["bajo"] += 1
        elif s >= 40:
            risk_dist["moderado"] += 1
        else:
            risk_dist["alto"] += 1

    # Crop distribution
    crops = (
        await db.execute(
            select(Parcela.crop_type, func.count(Parcela.id))
            .where(Parcela.crop_type.isnot(None))
            .group_by(Parcela.crop_type)
        )
    ).all()

    return {
        "total_farmers": total_farmers,
        "scored_farmers": scored_farmers,
        "avg_score": avg_score,
        "min_score": min_score,
        "max_score": max_score,
        "risk_distribution": risk_dist,
        "crop_distribution": {crop: count for crop, count in crops},
    }
