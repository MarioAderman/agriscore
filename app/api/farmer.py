"""Farmer API — endpoints for the farmer-facing React app."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_cognito_token
from app.dependencies import get_db
from app.models.database import (
    AgriScoreResult,
    Application,
    Challenge,
    ChallengeStatus,
    Farmer,
    Parcela,
)

router = APIRouter(dependencies=[Depends(verify_cognito_token)])


@router.get("/{phone}/profile")
async def get_farmer_profile(phone: str, db: AsyncSession = Depends(get_db)):
    """Farmer's own profile view."""
    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=404, detail="Agricultor no encontrado")

    parcela_result = await db.execute(select(Parcela).where(Parcela.farmer_id == farmer.id))
    parcela = parcela_result.scalar_one_or_none()

    return {
        "name": farmer.name,
        "phone": farmer.phone,
        "onboarded": farmer.onboarded,
        "registered_at": farmer.created_at.isoformat(),
        "parcela": {
            "latitude": parcela.latitude,
            "longitude": parcela.longitude,
            "crop_type": parcela.crop_type,
            "area_hectares": parcela.area_hectares,
        }
        if parcela
        else None,
    }


@router.get("/{phone}/agriscore")
async def get_farmer_agriscore(phone: str, db: AsyncSession = Depends(get_db)):
    """Farmer's current AgriScore and history."""
    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=404, detail="Agricultor no encontrado")

    scores = (
        await db.execute(
            select(AgriScoreResult, Application.created_at.label("app_created"))
            .join(Application, AgriScoreResult.application_id == Application.id)
            .where(Application.farmer_id == farmer.id)
            .order_by(AgriScoreResult.created_at.desc())
        )
    ).all()

    if not scores:
        return {"has_score": False, "message": "Aún no tienes un AgriScore."}

    latest = scores[0][0]
    return {
        "has_score": True,
        "current": {
            "total": round(latest.total_score, 1),
            "sub_productive": round(latest.sub_productive, 1),
            "sub_climate": round(latest.sub_climate, 1),
            "sub_behavioral": round(latest.sub_behavioral, 1),
            "sub_esg": round(latest.sub_esg, 1),
            "scored_at": latest.created_at.isoformat(),
            "risk_category": (
                "bajo" if latest.total_score >= 658 else "moderado" if latest.total_score >= 520 else "alto"
            ),
        },
        "history": [
            {
                "total": round(s.total_score, 1),
                "scored_at": s.created_at.isoformat(),
            }
            for s, _ in scores
        ],
    }


@router.get("/{phone}/challenges")
async def get_farmer_challenges(phone: str, db: AsyncSession = Depends(get_db)):
    """Farmer's active and completed gamification challenges."""
    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=404, detail="Agricultor no encontrado")

    challenges = (
        (await db.execute(select(Challenge).where(Challenge.farmer_id == farmer.id).order_by(Challenge.sent_at.desc())))
        .scalars()
        .all()
    )

    return {
        "total": len(challenges),
        "completed": sum(1 for c in challenges if c.status == ChallengeStatus.completed),
        "challenges": [
            {
                "id": str(c.id),
                "type": c.challenge_type,
                "status": c.status.value,
                "ai_tag": c.ai_tag,
                "sent_at": c.sent_at.isoformat(),
                "completed_at": c.completed_at.isoformat() if c.completed_at else None,
            }
            for c in challenges
        ],
    }


@router.get("/{phone}/satellite")
async def get_satellite_image(
    phone: str,
    type: str = Query("ndvi", pattern="^(ndvi|rgb)$"),
    db: AsyncSession = Depends(get_db),
):
    """Satellite image of the farmer's parcela. type: 'ndvi' (vegetation) or 'rgb' (true color)."""
    from app.pipeline.satellite import fetch_image

    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
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
