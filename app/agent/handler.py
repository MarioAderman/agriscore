"""Normalize incoming EvolutionAPI webhook payloads into a unified message format."""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IncomingMessage:
    """Normalized message from any WhatsApp input type."""
    phone: str           # Sender phone number (without @s.whatsapp.net)
    text: str | None     # Text content (or transcription for voice)
    image_url: str | None     # Direct URL for image
    audio_url: str | None     # Direct URL for audio/voice note
    document_url: str | None  # Direct URL for document
    latitude: float | None
    longitude: float | None
    message_type: str    # text, image, audio, location, document
    raw: dict            # Original payload for debugging


def parse_webhook(payload: dict) -> IncomingMessage | None:
    """Parse EvolutionAPI webhook payload into IncomingMessage.

    EvolutionAPI sends webhooks with event types. We care about MESSAGES_UPSERT
    which contains incoming messages.

    Returns None if the payload should be ignored (e.g., outgoing messages, status updates).
    """
    event = payload.get("event")

    # Only process incoming messages
    if event != "messages.upsert":
        logger.debug("Ignoring event: %s", event)
        return None

    data = payload.get("data", {})
    key = data.get("key", {})

    # Skip messages sent by us
    if key.get("fromMe", False):
        return None

    # Extract phone number from remoteJid (format: 5511999999999@s.whatsapp.net)
    remote_jid = key.get("remoteJid", "")
    if not remote_jid or "@g.us" in remote_jid:
        # Skip group messages
        return None
    phone = remote_jid.split("@")[0]

    message = data.get("message", {})

    # Determine message type and extract content
    if "conversation" in message:
        return IncomingMessage(
            phone=phone,
            text=message["conversation"],
            image_url=None,
            audio_url=None,
            document_url=None,
            latitude=None,
            longitude=None,
            message_type="text",
            raw=data,
        )

    if "extendedTextMessage" in message:
        return IncomingMessage(
            phone=phone,
            text=message["extendedTextMessage"].get("text", ""),
            image_url=None,
            audio_url=None,
            document_url=None,
            latitude=None,
            longitude=None,
            message_type="text",
            raw=data,
        )

    if "imageMessage" in message:
        img = message["imageMessage"]
        return IncomingMessage(
            phone=phone,
            text=img.get("caption"),
            image_url=img.get("url"),
            audio_url=None,
            document_url=None,
            latitude=None,
            longitude=None,
            message_type="image",
            raw=data,
        )

    if "audioMessage" in message:
        audio = message["audioMessage"]
        return IncomingMessage(
            phone=phone,
            text=None,
            image_url=None,
            audio_url=audio.get("url"),
            document_url=None,
            latitude=None,
            longitude=None,
            message_type="audio",
            raw=data,
        )

    if "locationMessage" in message:
        loc = message["locationMessage"]
        return IncomingMessage(
            phone=phone,
            text=loc.get("name") or loc.get("address"),
            image_url=None,
            audio_url=None,
            document_url=None,
            latitude=loc.get("degreesLatitude"),
            longitude=loc.get("degreesLongitude"),
            message_type="location",
            raw=data,
        )

    if "documentMessage" in message or "documentWithCaptionMessage" in message:
        doc = message.get("documentMessage") or message.get(
            "documentWithCaptionMessage", {}
        ).get("message", {}).get("documentMessage", {})
        return IncomingMessage(
            phone=phone,
            text=doc.get("caption") or doc.get("fileName"),
            image_url=None,
            audio_url=None,
            document_url=doc.get("url"),
            latitude=None,
            longitude=None,
            message_type="document",
            raw=data,
        )

    logger.warning("Unknown message type for phone %s: %s", phone, list(message.keys()))
    return None
