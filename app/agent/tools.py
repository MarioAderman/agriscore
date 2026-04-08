"""Tool definitions and executors for the AgriScore AI agent."""

import base64
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm import get_claude_client, get_claude_model
from app.models.database import (
    AgriScoreResult,
    Application,
    ApplicationStatus,
    Farmer,
    Parcela,
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
                "area_hectares": {
                    "type": "number",
                    "description": "Superficie de la parcela en hectáreas",
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
    {
        "name": "extract_document",
        "description": "Extrae datos estructurados de un documento enviado (constancia fiscal, certificado parcelario, INE, etc.) usando visión por computadora. Usar cuando el agricultor envía un documento o foto.",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_url": {
                    "type": "string",
                    "description": "URL o ruta local del documento a extraer",
                },
                "document_type": {
                    "type": "string",
                    "description": "Tipo de documento (constancia_fiscal, certificado_parcelario, ine, otro)",
                },
            },
            "required": ["document_url"],
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
        elif tool_name == "extract_document":
            return await _extract_document(phone, tool_input, db)
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

    # If crop_type or area_hectares provided, update or create the first parcela
    crop_type = inputs.get("crop_type")
    area_hectares = inputs.get("area_hectares")
    if crop_type or area_hectares:
        result = await db.execute(select(Parcela).where(Parcela.farmer_id == farmer.id))
        parcela = result.scalar_one_or_none()
        if parcela:
            if crop_type:
                parcela.crop_type = crop_type
            if area_hectares:
                parcela.area_hectares = area_hectares
        else:
            parcela = Parcela(
                farmer_id=farmer.id,
                crop_type=crop_type,
                area_hectares=area_hectares,
            )
            db.add(parcela)

    await db.commit()
    parts = [f"Perfil guardado: {farmer.name}"]
    if crop_type:
        parts.append(f"cultivo: {crop_type}")
    if area_hectares:
        parts.append(f"área: {area_hectares} ha")
    return ", ".join(parts)


async def _save_location(phone: str, inputs: dict, db: AsyncSession) -> str:
    result = await db.execute(select(Farmer).where(Farmer.phone == phone))
    farmer = result.scalar_one_or_none()

    if not farmer:
        return "Error: primero necesito el nombre del agricultor."

    lat = inputs["latitude"]
    lon = inputs["longitude"]

    result = await db.execute(select(Parcela).where(Parcela.farmer_id == farmer.id))
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

    result = await db.execute(select(Parcela).where(Parcela.farmer_id == farmer.id))
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


async def _extract_document(phone: str, inputs: dict, db: AsyncSession) -> str:
    """Extract structured data from a document using Claude Vision."""
    doc_url = inputs["document_url"]
    doc_type = inputs.get("document_type", "desconocido")

    # Read file bytes
    path = Path(doc_url)
    if path.exists():
        file_bytes = path.read_bytes()
        if path.suffix.lower() == ".pdf":
            media_type = "application/pdf"
        elif path.suffix.lower() in (".jpg", ".jpeg"):
            media_type = "image/jpeg"
        elif path.suffix.lower() == ".png":
            media_type = "image/png"
        else:
            media_type = "application/pdf"
    else:
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(doc_url)
            resp.raise_for_status()
            file_bytes = resp.content
            media_type = resp.headers.get("content-type", "application/pdf").split(";")[0]

    b64_data = base64.b64encode(file_bytes).decode()

    # Build content block based on media type
    if media_type == "application/pdf":
        source_block = {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": b64_data},
        }
    else:
        source_block = {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64_data},
        }

    extraction_prompt = (
        f"Extrae todos los datos relevantes de este documento ({doc_type}). "
        "Responde SOLO con un JSON válido con los campos que encuentres:\n"
        '- "nombre": nombre completo de la persona\n'
        '- "rfc": RFC (si aparece)\n'
        '- "curp": CURP (si aparece)\n'
        '- "domicilio": dirección completa\n'
        '- "estado": estado de México\n'
        '- "municipio": municipio\n'
        '- "cultivos": lista de cultivos mencionados con porcentajes si los hay\n'
        '- "area_hectareas": superficie en hectáreas\n'
        '- "latitud": latitud (si aparece coordenadas GPS)\n'
        '- "longitud": longitud (si aparece coordenadas GPS)\n'
        '- "numero_parcela": número de parcela\n'
        '- "ejido": nombre del ejido\n'
        '- "tipo_documento": tipo de documento identificado\n'
        "Omite campos que no encuentres. Solo el JSON, sin markdown ni explicaciones."
    )

    try:
        response = await get_claude_client().messages.create(
            model=get_claude_model(),
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [source_block, {"type": "text", "text": extraction_prompt}],
                }
            ],
        )
        extracted = response.content[0].text
        logger.info("Document extracted for %s: %s", phone, extracted[:200])
        return f"Datos extraídos del documento:\n{extracted}"
    except Exception as e:
        logger.exception("Document extraction failed for %s", phone)
        return f"Error al extraer datos del documento: {e}"
