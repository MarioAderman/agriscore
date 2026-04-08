"""
Option A — Text-only demo script for AgriScore hackathon.

Simulates a farmer onboarding via WhatsApp text messages + location.
No document processing needed — all data provided via text.

Usage:
    uv run python scripts/test_demo.py [--base-url http://localhost:8000]

The server must be running:
    uv run uvicorn app.main:app --reload
"""

import argparse
import asyncio
import sys

import httpx

DEFAULT_PHONE = "5219611234567"  # Chiapas area code


def make_text_payload(phone: str, text: str) -> dict:
    return {
        "event": "messages.upsert",
        "instance": "agriscore",
        "data": {
            "key": {
                "remoteJid": f"{phone}@s.whatsapp.net",
                "fromMe": False,
                "id": "demo-text-msg",
            },
            "message": {"conversation": text},
            "messageType": "conversation",
        },
    }


def make_location_payload(phone: str, lat: float, lon: float) -> dict:
    return {
        "event": "messages.upsert",
        "instance": "agriscore",
        "data": {
            "key": {
                "remoteJid": f"{phone}@s.whatsapp.net",
                "fromMe": False,
                "id": "demo-loc-msg",
            },
            "message": {
                "locationMessage": {
                    "degreesLatitude": lat,
                    "degreesLongitude": lon,
                    "name": "Parcela 287, Ejido El Ocote",
                },
            },
            "messageType": "locationMessage",
        },
    }


async def send(client: httpx.AsyncClient, base_url: str, payload: dict) -> dict:
    r = await client.post(f"{base_url}/api/webhook/whatsapp", json=payload)
    r.raise_for_status()
    return r.json()


async def run_demo(base_url: str):
    phone = DEFAULT_PHONE

    # José Daniel Escutia — La Reserva del Ocote, Chiapas
    steps = [
        ("text", "Hola, buenos días", 4),
        ("text", "Me llamo José Daniel Escutia Barragán y siembro maíz", 5),
        ("location", (16.8912, -93.5478), 5),
        ("text", "Sí, evalúa mi parcela por favor", 20),
        ("text", "¿Cuál es mi AgriScore?", 5),
    ]

    print(f"\n{'='*60}")
    print("  AgriScore Demo — Option A (text-only)")
    print("  Farmer: José Daniel Escutia Barragán")
    print(f"  Phone:  {phone}")
    print(f"  Server: {base_url}")
    print(f"{'='*60}\n")

    async with httpx.AsyncClient(timeout=60) as client:
        # Check server is up
        try:
            await client.get(f"{base_url}/health")
        except httpx.ConnectError:
            print(f"ERROR: Cannot connect to {base_url}")
            print("Start the server: uv run uvicorn app.main:app --reload")
            sys.exit(1)

        for i, step in enumerate(steps, 1):
            msg_type = step[0]
            wait = step[-1]

            if msg_type == "text":
                text = step[1]
                print(f"[{i}/{len(steps)}] 💬 \"{text}\"")
                payload = make_text_payload(phone, text)
            else:
                lat, lon = step[1]
                print(f"[{i}/{len(steps)}] 📍 Location ({lat}, {lon})")
                payload = make_location_payload(phone, lat, lon)

            result = await send(client, base_url, payload)
            print(f"         → webhook: {result}")

            if wait > 0:
                print(f"         ⏳ Waiting {wait}s...")
                await asyncio.sleep(wait)
            print()

    print(f"{'='*60}")
    print("  Demo complete! Check server logs for agent responses.")
    print()
    print("  Verify:")
    print(f'  curl -H "x-api-key: demo-bank-key" {base_url}/api/bank/farmers')
    print(f"  curl {base_url}/api/farmer/{phone}/agriscore")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgriScore demo — text-only flow")
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()
    asyncio.run(run_demo(args.base_url))
