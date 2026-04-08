"""Local test for Lambda pipeline handlers.

Runs each handler sequentially against a local PostgreSQL (via docker-compose)
and real external APIs. Validates the full pipeline end-to-end.

Usage:
  1. docker compose up db -d
  2. uv run python scripts/test_lambda_local.py
"""

import json
import os
import sys
import uuid

import psycopg2

# Load .env
from dotenv import load_dotenv

load_dotenv()

# Use DATABASE_URL from .env (already loaded by dotenv)
LOCAL_DB = os.environ["DATABASE_URL"]

# Add infra/lambda to path so handlers can import shared/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "infra", "lambda"))
# Add project root so app/ package is importable (for pipeline modules)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def setup_db():
    """Create tables and seed a test farmer + parcela + application."""
    conn = psycopg2.connect(LOCAL_DB)
    conn.autocommit = True
    cur = conn.cursor()

    # Create tables (idempotent)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id UUID PRIMARY KEY,
            phone VARCHAR(20) UNIQUE,
            name VARCHAR(100),
            onboarded BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parcelas (
            id UUID PRIMARY KEY,
            farmer_id UUID REFERENCES farmers(id),
            name VARCHAR(100),
            latitude FLOAT,
            longitude FLOAT,
            area_hectares FLOAT,
            crop_type VARCHAR(50),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id UUID PRIMARY KEY,
            farmer_id UUID REFERENCES farmers(id),
            parcela_id UUID REFERENCES parcelas(id),
            status VARCHAR(20) DEFAULT 'pending',
            step_functions_arn VARCHAR(256),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            completed_at TIMESTAMPTZ
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS satellite_data (
            id UUID PRIMARY KEY,
            application_id UUID UNIQUE REFERENCES applications(id),
            ndvi_mean FLOAT,
            ndvi_tile_s3_key VARCHAR(256),
            fetched_at TIMESTAMPTZ DEFAULT NOW(),
            raw_data JSONB
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS climate_data (
            id UUID PRIMARY KEY,
            application_id UUID UNIQUE REFERENCES applications(id),
            avg_temperature FLOAT,
            total_precipitation FLOAT,
            et0 FLOAT,
            soil_moisture FLOAT,
            fetched_at TIMESTAMPTZ DEFAULT NOW(),
            raw_data JSONB
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS socioeconomic_data (
            id UUID PRIMARY KEY,
            application_id UUID UNIQUE REFERENCES applications(id),
            population INTEGER,
            agri_establishments INTEGER,
            fetched_at TIMESTAMPTZ DEFAULT NOW(),
            raw_data JSONB
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agriscore_results (
            id UUID PRIMARY KEY,
            application_id UUID UNIQUE REFERENCES applications(id),
            total_score FLOAT,
            sub_productive FLOAT,
            sub_climate FLOAT,
            sub_behavioral FLOAT,
            sub_esg FLOAT,
            explanation TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    # Seed test data — a farmer in Jalisco with maize
    farmer_id = str(uuid.uuid4())
    parcela_id = str(uuid.uuid4())
    application_id = str(uuid.uuid4())

    # Clean previous test data (respect FK order)
    cur.execute("DELETE FROM agriscore_results")
    cur.execute("DELETE FROM socioeconomic_data")
    cur.execute("DELETE FROM climate_data")
    cur.execute("DELETE FROM satellite_data")
    cur.execute("DELETE FROM applications")
    cur.execute("DELETE FROM challenges")
    cur.execute("DELETE FROM conversations")
    cur.execute("DELETE FROM parcelas")
    cur.execute("DELETE FROM farmers")

    cur.execute(
        "INSERT INTO farmers (id, phone, name, onboarded, created_at) VALUES (%s, %s, %s, %s, NOW())",
        (farmer_id, "+5213312345678", "Juan Prueba", True),
    )
    cur.execute(
        "INSERT INTO parcelas (id, farmer_id, name, latitude, longitude, area_hectares, crop_type, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())",
        (parcela_id, farmer_id, "Parcela Test", 20.6597, -103.3496, 8.5, "maiz"),
    )
    cur.execute(
        "INSERT INTO applications (id, farmer_id, parcela_id, status, created_at) VALUES (%s, %s, %s, %s, NOW())",
        (application_id, farmer_id, parcela_id, "processing"),
    )

    cur.close()
    conn.close()

    print(f"  Farmer:      {farmer_id}")
    print(f"  Parcela:     {parcela_id} (Guadalajara, Jalisco — maiz)")
    print(f"  Application: {application_id}")
    return application_id


def run_handler(name, module_path, application_id):
    """Import and run a Lambda handler, report result."""
    print(f"\n{'─' * 50}")
    print(f"  Step: {name}")
    print(f"{'─' * 50}")

    try:
        # Dynamic import of handler module
        import importlib.util

        spec = importlib.util.spec_from_file_location(name, module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        event = {"application_id": application_id}
        result = mod.handler(event, None)

        print(f"  Result: {json.dumps(result, indent=2, default=str)}")
        print("  Status: PASS")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        print("  Status: FAIL")
        return False


def main():
    handlers_dir = os.path.join(os.path.dirname(__file__), "..", "infra", "lambda", "handlers")

    print("=" * 50)
    print("  Lambda Pipeline Local Test")
    print("=" * 50)
    print()

    # Step 0: Setup
    print("Setting up test data...")
    application_id = setup_db()
    print()

    # Steps in pipeline order
    steps = [
        ("1. Extract Docs (Claude LLM)", "extract_docs.py"),
        ("2. Fetch Satellite (Sentinel Hub)", "fetch_satellite.py"),
        ("3a. Fetch Climate (Open-Meteo + NASA)", "fetch_climate.py"),
        ("3b. Fetch Socioeconomic (INEGI)", "fetch_socioeconomic.py"),
        ("4. Calculate Score (ML model)", "calculate_score.py"),
        ("5. Generate Expediente (WhatsApp)", "generate_expediente.py"),
    ]

    results = {}
    for step_name, filename in steps:
        path = os.path.join(handlers_dir, filename)
        passed = run_handler(step_name, path, application_id)
        results[step_name] = passed

        # Stop if a critical step fails (scoring needs satellite + climate data)
        if not passed and "Extract" in step_name:
            print("\n  Extract failed — pipeline cannot continue without GPS validation.")
            break

    # Summary
    print(f"\n{'=' * 50}")
    print("  Summary")
    print(f"{'=' * 50}")
    for step, passed in results.items():
        icon = "PASS" if passed else "FAIL"
        print(f"  [{icon}] {step}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n  {passed}/{total} steps passed")


if __name__ == "__main__":
    main()
