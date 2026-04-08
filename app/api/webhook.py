import logging

from fastapi import APIRouter, BackgroundTasks, Request

from app.agent.agent import run_agent
from app.agent.handler import IncomingMessage, parse_webhook
from app.services import evolution

router = APIRouter()
logger = logging.getLogger(__name__)


async def _process_message(msg: IncomingMessage):
    """Process a message in the background so the webhook returns 200 immediately."""
    from app.db.connection import async_session

    async with async_session() as db:
        try:
            # Build text input for the agent
            if msg.message_type == "text":
                user_text = msg.text or ""
            elif msg.message_type == "location":
                user_text = f"[Ubicación compartida: lat={msg.latitude}, lon={msg.longitude}]"
            elif msg.message_type == "image":
                user_text = f"[Foto enviada]{': ' + msg.text if msg.text else ''}"
            elif msg.message_type == "audio":
                # TODO: Whisper STT transcription
                user_text = "[Nota de voz recibida — transcripción pendiente]"
            elif msg.message_type == "document":
                user_text = f"[Documento enviado: {msg.text or 'sin nombre'}]"
            else:
                user_text = f"[Mensaje tipo {msg.message_type}]"

            # Run the AI agent
            response_text = await run_agent(
                phone=msg.phone,
                user_text=user_text,
                message_type=msg.message_type,
                db=db,
            )

            # Send response back via WhatsApp
            if response_text:
                await evolution.send_text(msg.phone, response_text)

        except Exception:
            logger.exception("Error processing message from %s", msg.phone)
            await evolution.send_text(
                msg.phone,
                "Disculpa, tuve un problema procesando tu mensaje. ¿Puedes intentar de nuevo? 🙏",
            )


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receives messages from EvolutionAPI and routes to AI agent."""
    payload = await request.json()
    logger.info("WhatsApp webhook received: %s", payload.get("event", "unknown"))

    msg = parse_webhook(payload)
    if msg is None:
        return {"status": "ignored"}

    logger.info("Message from %s [%s]: %s", msg.phone, msg.message_type, (msg.text or "")[:50])

    # Process in background so we return 200 to EvolutionAPI immediately
    background_tasks.add_task(_process_message, msg)

    return {"status": "processing"}
