"""HTTP client for EvolutionAPI — send messages via WhatsApp."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = settings.evolution_api_url
INSTANCE = settings.evolution_instance_name
HEADERS = {
    "Content-Type": "application/json",
    "apikey": settings.evolution_api_key,
}


async def send_text(phone: str, text: str) -> dict:
    """Send a text message via WhatsApp."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/message/sendText/{INSTANCE}",
            headers=HEADERS,
            json={"number": phone, "text": text},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


async def send_media(
    phone: str,
    media_url: str,
    media_type: str = "image",
    mimetype: str = "image/jpeg",
    caption: str = "",
    filename: str = "file",
) -> dict:
    """Send a media message (image, video, document)."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/message/sendMedia/{INSTANCE}",
            headers=HEADERS,
            json={
                "number": phone,
                "mediatype": media_type,
                "mimetype": mimetype,
                "caption": caption,
                "media": media_url,
                "fileName": filename,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


async def send_audio(phone: str, audio_url: str) -> dict:
    """Send an audio message (voice note)."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/message/sendWhatsAppAudio/{INSTANCE}",
            headers=HEADERS,
            json={"number": phone, "audio": audio_url},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


async def send_location(
    phone: str, latitude: float, longitude: float, name: str = "", address: str = ""
) -> dict:
    """Send a location pin."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/message/sendLocation/{INSTANCE}",
            headers=HEADERS,
            json={
                "number": phone,
                "latitude": latitude,
                "longitude": longitude,
                "name": name,
                "address": address,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
