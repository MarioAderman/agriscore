"""
Mock WhatsApp webhook test — simulates EvolutionAPI events hitting the FastAPI server.

Usage:
    uv run python scripts/test_webhook.py [--phone 5212221234567] [--interactive]

The server must be running:
    uv run uvicorn app.main:app --reload

Examples:
    # Run a fixed onboarding script
    uv run python scripts/test_webhook.py

    # Interactive REPL — type messages as if you're the farmer
    uv run python scripts/test_webhook.py --interactive
"""

import argparse
import asyncio

import httpx

BASE_URL = "http://localhost:8000"
DEFAULT_PHONE = "5212221234567"  # Culiacán area code


def make_text_payload(phone: str, text: str) -> dict:
    return {
        "event": "messages.upsert",
        "instance": "agriscore",
        "data": {
            "key": {
                "remoteJid": f"{phone}@s.whatsapp.net",
                "fromMe": False,
                "id": "mock-msg-id",
            },
            "message": {
                "conversation": text,
            },
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
                "id": "mock-loc-id",
            },
            "message": {
                "locationMessage": {
                    "degreesLatitude": lat,
                    "degreesLongitude": lon,
                    "name": "Mi parcela",
                },
            },
            "messageType": "locationMessage",
        },
    }


async def send_message(client: httpx.AsyncClient, payload: dict) -> dict:
    r = await client.post(f"{BASE_URL}/api/webhook/whatsapp", json=payload)
    r.raise_for_status()
    return r.json()


async def run_script(phone: str):
    """Run a fixed onboarding script to test the full flow."""
    print(f"\n=== Mock WhatsApp Test — phone: {phone} ===\n")

    # Fixed test script: Culiacán, Sinaloa corn farmer
    steps = [
        ("text", "Hola", None),
        ("text", "Me llamo Juan Torres y siembro maíz", None),
        # Culiacán coordinates
        ("location", None, (24.7994, -107.3898)),
        ("text", "¿Puedes evaluar mi parcela?", None),
        ("text", "¿Cuál es mi AgriScore?", None),
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        for i, (msg_type, text, coords) in enumerate(steps, 1):
            print(f"[{i}/{len(steps)}] Sending: ", end="")
            if msg_type == "text":
                print(f'"{text}"')
                payload = make_text_payload(phone, text)
            else:
                print(f"location ({coords[0]}, {coords[1]})")
                payload = make_location_payload(phone, coords[0], coords[1])

            result = await send_message(client, payload)
            print(f"       Webhook response: {result}")

            # Wait for background task to process
            await asyncio.sleep(3)
            print()

    print("=== Script complete. Check server logs for agent responses. ===")
    print("Note: evolution.send_text() calls will fail if EvolutionAPI isn't running.")
    print("That's expected — check logs for the response text the agent would have sent.")


async def run_interactive(phone: str):
    """Interactive REPL for testing the agent."""
    print(f"\n=== Interactive WhatsApp Mock — phone: {phone} ===")
    print("Commands: /quit, /location <lat> <lon>")
    print("Everything else is sent as a WhatsApp text message.\n")

    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            try:
                text = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break

            if not text:
                continue
            if text == "/quit":
                break

            if text.startswith("/location "):
                parts = text.split()
                if len(parts) != 3:
                    print("Usage: /location <lat> <lon>")
                    continue
                lat, lon = float(parts[1]), float(parts[2])
                payload = make_location_payload(phone, lat, lon)
            else:
                payload = make_text_payload(phone, text)

            try:
                result = await send_message(client, payload)
                print(f"[webhook: {result}]")
                # Brief pause so background task can start processing
                await asyncio.sleep(0.2)
            except httpx.ConnectError:
                print("ERROR: Cannot connect to server. Is `uv run uvicorn app.main:app --reload` running?")
            except Exception as e:
                print(f"ERROR: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock WhatsApp webhook for local testing")
    parser.add_argument("--phone", default=DEFAULT_PHONE, help="Simulated sender phone number")
    parser.add_argument("--interactive", action="store_true", help="Interactive REPL mode")
    args = parser.parse_args()

    if args.interactive:
        asyncio.run(run_interactive(args.phone))
    else:
        asyncio.run(run_script(args.phone))
