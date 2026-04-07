"""Tool definitions and executors for the AgriScore AI agent."""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    Farmer,
    Parcela,
    Application,
    AgriScoreResult,
    ApplicationStatus,
)

logger = logging.getLogger(__name__)

# --- Tool definitions for Anthropic SDK ---

TOOL_DEFINITIONS = [
    {
        "name": "save_farmer_profile",
        "description": "Guarda o actualiza el perfil del agricultor con su nombre y tipo de cultivo. Usar cuando el agricultor proporciona su nombre y/o cultivo durante el onboarding.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Nombre del agricultor",
                },
                "crop_type": {
                    "type": "string",
                    "description": "Tipo de cultivo principal (ej: maíz, frijol, chile, tomate, sorgo)",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "save_location",
        "description": "Guarda la ubicación GPS de la parcela del agricultor. Usar cuando el agricultor comparte su ubicación.",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitud de la parcela",
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitud de la parcela",
                },
            },
            "required": ["latitude", "longitude"],
        },
    },
    {
        "name": "trigger_evaluation",
        "description": "Inicia el pipeline de evaluación AgriScore para el agricultor. Solo usar cuando el agricultor ya tiene perfil y ubicación GPS guardados.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_agriscore",
        "description": "Consulta el AgriScore actual del agricultor, incluyendo sub-puntajes. Usar cuando el agricultor pregunta por su score.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# --- Tool executors ---

async def execute_tool(
    tool_name: str,
    tool_input: dict,
    phone: str,
    db: AsyncSession,
) -> str:
    """Execute a tool and return the result as a string for the agent."""
    try:
        if tool_name == "save_farmer_profile":
            return await _save_farmer_profile(phone, tool_input, db)
        elif tool_name == "save_location":
            return await _save_location(phone, tool_input, db)
        elif tool_name == "trigger_evaluation":
            return await _trigger_evaluation(phone, db)
        elif tool_name == "get_agriscore":
            return await _get_agriscore(phone, db)
        else:
            return f"Error: herramienta desconocida '{tool_name}'"
    except Exception as e:
        logger.exception("Tool execution error: %s", tool_name)
        return f"Error ejecutando {tool_name}: {str(e)}"


async def _save_farmer_profile(phone: str, inputs: dict, db: AsyncSession) -> str:
    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = result.scalar_one_or_none()

    if farmer:
        if inputs.get("name"):
            farmer.name = inputs["name"]
        farmer.onboarded = True
    else:
        farmer = Farmer(
            phone=phone,
            name=inputs.get("name"),
            onboarded=True,
        )
        db.add(farmer)

    await db.flush()

    # If crop_type provided, update or create the first parcela
    crop_type = inputs.get("crop_type")
    if crop_type:
        result = await db.execute(
            select(Parcela).where(Parcela.farmer_id == farmer.id)
        )
        parcela = result.scalar_one_or_none()
        if parcela:
            parcela.crop_type = crop_type
        else:
            parcela = Parcela(farmer_id=farmer.id, crop_type=crop_type)
            db.add(parcela)

    await db.commit()
    return f"Perfil guardado: {farmer.name}, cultivo: {crop_type or 'no especificado'}"


async def _save_location(phone: str, inputs: dict, db: AsyncSession) -> str:
    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = result.scalar_one_or_none()

    if not farmer:
        return "Error: primero necesito el nombre del agricultor."

    lat = inputs["latitude"]
    lon = inputs["longitude"]

    result = await db.execute(
        select(Parcela).where(Parcela.farmer_id == farmer.id)
    )
    parcela = result.scalar_one_or_none()

    if parcela:
        parcela.latitude = lat
        parcela.longitude = lon
    else:
        parcela = Parcela(farmer_id=farmer.id, latitude=lat, longitude=lon)
        db.add(parcela)

    await db.commit()
    return f"Ubicación guardada: {lat:.4f}, {lon:.4f}"


async def _trigger_evaluation(phone: str, db: AsyncSession) -> str:
    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = result.scalar_one_or_none()
    if not farmer:
        return "Error: agricultor no encontrado."

    result = await db.execute(
        select(Parcela).where(Parcela.farmer_id == farmer.id)
    )
    parcela = result.scalar_one_or_none()
    if not parcela or not parcela.latitude:
        return "Error: necesito la ubicación GPS de la parcela antes de evaluar."

    # Create application record
    application = Application(
        farmer_id=farmer.id,
        parcela_id=parcela.id,
        status=ApplicationStatus.processing,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)

    logger.info(
        "Evaluation triggered for farmer %s, application %s",
        farmer.id,
        application.id,
    )

    # Trigger pipeline asynchronously (fire-and-forget)
    import asyncio
    from app.pipeline.orchestrator import trigger_step_functions

    asyncio.create_task(trigger_step_functions(str(application.id)))

    return (
        f"Evaluación iniciada (ID: {application.id}). "
        f"Se están consultando datos satelitales y climáticos para la ubicación "
        f"{parcela.latitude:.4f}, {parcela.longitude:.4f}. "
        f"El proceso tarda aproximadamente 30-60 segundos. "
        f"Te avisaré cuando esté listo."
    )


async def _get_agriscore(phone: str, db: AsyncSession) -> str:
    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = result.scalar_one_or_none()
    if not farmer:
        return "Error: agricultor no encontrado."

    # Get the most recent completed application with score
    result = await db.execute(
        select(AgriScoreResult)
        .join(Application)
        .where(Application.farmer_id == farmer.id)
        .order_by(AgriScoreResult.created_at.desc())
        .limit(1)
    )
    score = result.scalar_one_or_none()

    if not score:
        return "Aún no tienes un AgriScore. ¿Quieres que iniciemos la evaluación?"

    return (
        f"AgriScore: {score.total_score:.0f}/100\n"
        f"- Productivo: {score.sub_productive:.0f}/100\n"
        f"- Climático: {score.sub_climate:.0f}/100\n"
        f"- Comportamiento: {score.sub_behavioral:.0f}/100\n"
        f"- ESG: {score.sub_esg:.0f}/100\n"
        f"Fecha: {score.created_at.strftime('%d/%m/%Y')}"
    )
