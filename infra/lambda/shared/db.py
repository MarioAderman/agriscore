"""Shared DB helpers for Lambda handlers — sync psycopg2."""

import json
import os
import uuid

import psycopg2
import psycopg2.extras

# Register UUID adapter for psycopg2
psycopg2.extras.register_uuid()


def get_conn():
    """Return a new psycopg2 connection from DATABASE_URL."""
    return psycopg2.connect(os.environ["DATABASE_URL"])


def get_application(conn, application_id: str) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, farmer_id, parcela_id, status FROM applications WHERE id = %s",
            (application_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_parcela(conn, parcela_id) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, latitude, longitude, area_hectares, crop_type FROM parcelas WHERE id = %s",
            (parcela_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_farmer(conn, farmer_id) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, phone, name FROM farmers WHERE id = %s",
            (farmer_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def insert_satellite_data(conn, application_id, ndvi_mean: float, raw_data: dict):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO satellite_data (id, application_id, ndvi_mean, raw_data, fetched_at)
               VALUES (%s, %s, %s, %s, NOW())""",
            (str(uuid.uuid4()), str(application_id), ndvi_mean, json.dumps(raw_data)),
        )
    conn.commit()


def insert_climate_data(conn, application_id, avg_temperature, total_precipitation, et0, soil_moisture, raw_data):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO climate_data (id, application_id, avg_temperature, total_precipitation, et0, soil_moisture, raw_data, fetched_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
            (
                str(uuid.uuid4()),
                str(application_id),
                avg_temperature,
                total_precipitation,
                et0,
                soil_moisture,
                json.dumps(raw_data),
            ),
        )
    conn.commit()


def insert_socioeconomic_data(conn, application_id, population, agri_establishments, raw_data):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO socioeconomic_data (id, application_id, population, agri_establishments, raw_data, fetched_at)
               VALUES (%s, %s, %s, %s, %s, NOW())""",
            (
                str(uuid.uuid4()),
                str(application_id),
                population,
                agri_establishments,
                json.dumps(raw_data),
            ),
        )
    conn.commit()


def insert_agriscore_result(conn, application_id, total_score, sub_productive, sub_climate, sub_behavioral, sub_esg):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO agriscore_results (id, application_id, total_score, sub_productive, sub_climate, sub_behavioral, sub_esg, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
            (
                str(uuid.uuid4()),
                str(application_id),
                total_score,
                sub_productive,
                sub_climate,
                sub_behavioral,
                sub_esg,
            ),
        )
    conn.commit()


def get_satellite_data(conn, application_id) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM satellite_data WHERE application_id = %s", (str(application_id),))
        row = cur.fetchone()
        return dict(row) if row else None


def get_climate_data(conn, application_id) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM climate_data WHERE application_id = %s", (str(application_id),))
        row = cur.fetchone()
        return dict(row) if row else None


def get_socioeconomic_data(conn, application_id) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM socioeconomic_data WHERE application_id = %s", (str(application_id),))
        row = cur.fetchone()
        return dict(row) if row else None


def get_agriscore_result(conn, application_id) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM agriscore_results WHERE application_id = %s", (str(application_id),))
        row = cur.fetchone()
        return dict(row) if row else None


def mark_application_completed(conn, application_id):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE applications SET status = 'completed', completed_at = NOW() WHERE id = %s",
            (str(application_id),),
        )
    conn.commit()
