"""HTTP client for EvolutionAPI — send messages via WhatsApp."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = settings.evolutionapi_url
INSTANCE = settings.evolution_instance_name
HEADERS = {
    "Content-Type": "application/json",
    "apikey": settings.evolutionapi_authentication_api_key,
}


async def _post(path: str, body: dict) -> dict:
    """Internal POST helper. Returns empty dict and logs on connection failure."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}{path}",
                headers=HEADERS,
                json=body,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        logger.warning("EvolutionAPI not reachable at %s — message not delivered", BASE_URL)
        return {}
    except httpx.HTTPStatusError as e:
        logger.warning("EvolutionAPI error %s: %s", e.response.status_code, e.response.text[:200])
        return {}


async def send_text(phone: str, text: str) -> dict:
    """Send a text message via WhatsApp."""
    return await _post(
        f"/message/sendText/{INSTANCE}",
        {"number": phone, "text": text},
    )


async def send_media(
    phone: str,
    media_url: str,
    media_type: str = "image",
    mimetype: str = "image/jpeg",
    caption: str = "",
    filename: str = "file",
) -> dict:
    """Send a media message (image, video, document)."""
    return await _post(
        f"/message/sendMedia/{INSTANCE}",
        {
            "number": phone,
            "mediatype": media_type,
            "mimetype": mimetype,
            "caption": caption,
            "media": media_url,
            "fileName": filename,
        },
    )


async def send_audio(phone: str, audio_url: str) -> dict:
    """Send an audio message (voice note)."""
    return await _post(
        f"/message/sendWhatsAppAudio/{INSTANCE}",
        {"number": phone, "audio": audio_url},
    )


async def send_location(
    phone: str, latitude: float, longitude: float, name: str = "", address: str = ""
) -> dict:
    """Send a location pin."""
    return await _post(
        f"/message/sendLocation/{INSTANCE}",
        {
            "number": phone,
            "latitude": latitude,
            "longitude": longitude,
            "name": name,
            "address": address,
        },
    )
