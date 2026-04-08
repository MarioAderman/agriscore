"""
Option B — Document processing demo script for AgriScore hackathon.

Simulates a farmer sending PDFs via WhatsApp. The agent extracts data
using Claude Vision and processes the full evaluation pipeline.

Usage:
    uv run python scripts/test_demo_docs.py [--base-url http://localhost:8000]

Requires:
    - Server running: uv run uvicorn app.main:app --reload
    - Demo PDFs: docs/demo/constancia_fiscal_escutia.pdf, docs/demo/certificado_parcelario_escutia.pdf
    - ANTHROPIC_API_KEY set in .env (for Claude Vision extraction)
"""

import argparse
import asyncio
import os
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
                "id": "demo-doc-text",
            },
            "message": {"conversation": text},
            "messageType": "conversation",
        },
    }


def make_document_payload(phone: str, filename: str, doc_path: str) -> dict:
    """Simulate a WhatsApp document message with a local file path as URL."""
    return {
        "event": "messages.upsert",
        "instance": "agriscore",
        "data": {
            "key": {
                "remoteJid": f"{phone}@s.whatsapp.net",
                "fromMe": False,
                "id": "demo-doc-file",
            },
            "message": {
                "documentMessage": {
                    "url": doc_path,
                    "fileName": filename,
                    "caption": filename,
                    "mimetype": "application/pdf",
                },
            },
            "messageType": "documentMessage",
        },
    }


async def send(client: httpx.AsyncClient, base_url: str, payload: dict) -> dict:
    r = await client.post(f"{base_url}/api/webhook/whatsapp", json=payload)
    r.raise_for_status()
    return r.json()


async def run_demo(base_url: str):
    phone = DEFAULT_PHONE

    # Resolve demo PDF paths relative to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    constancia_path = os.path.join(project_root, "docs", "demo", "constancia_fiscal_escutia.pdf")
    certificado_path = os.path.join(project_root, "docs", "demo", "certificado_parcelario_escutia.pdf")

    for path in [constancia_path, certificado_path]:
        if not os.path.exists(path):
            print(f"ERROR: Demo PDF not found: {path}")
            print("Run: uv run python scripts/generate_demo_docs.py")
            sys.exit(1)

    steps = [
        ("text", "Hola, buenos días", 5),
        ("document", ("constancia_fiscal_escutia.pdf", constancia_path), 15),
        ("document", ("certificado_parcelario_escutia.pdf", certificado_path), 15),
        ("text", "Sí, los datos están correctos", 8),
        ("text", "Evalúa mi parcela por favor", 25),
        ("text", "¿Cuál es mi AgriScore?", 5),
    ]

    print(f"\n{'='*60}")
    print("  AgriScore Demo — Option B (document processing)")
    print("  Farmer: José Daniel Escutia Barragán")
    print(f"  Phone:  {phone}")
    print(f"  Server: {base_url}")
    print(f"  PDFs:   {constancia_path}")
    print(f"          {certificado_path}")
    print(f"{'='*60}\n")

    async with httpx.AsyncClient(timeout=120) as client:
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
            elif msg_type == "document":
                filename, doc_path = step[1]
                print(f"[{i}/{len(steps)}] 📄 Document: {filename}")
                payload = make_document_payload(phone, filename, doc_path)

            result = await send(client, base_url, payload)
            print(f"         → webhook: {result}")

            if wait > 0:
                print(f"         ⏳ Waiting {wait}s (Claude Vision extraction)...")
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
    parser = argparse.ArgumentParser(description="AgriScore demo — document processing flow")
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()
    asyncio.run(run_demo(args.base_url))
