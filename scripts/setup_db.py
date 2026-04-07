"""Set up the agriscore database, user, and PostGIS extension.

Reads POSTGRES_PSSWD from .env for the postgres superuser.
Creates: user 'agriscore', database 'agriscore', enables PostGIS.

Usage: uv run python scripts/setup_db.py
"""

import os
import secrets
import string

import psycopg2
from dotenv import load_dotenv

load_dotenv()

POSTGRES_PSSWD = os.getenv("POSTGRES_PSSWD")
if not POSTGRES_PSSWD:
    print("ERROR: POSTGRES_PSSWD not found in .env")
    exit(1)


def generate_password(length=24):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def main():
    # Connect as superuser
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password=POSTGRES_PSSWD,
        dbname="postgres",
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Generate a password for the agriscore user
    agriscore_password = generate_password()

    # Create user if not exists
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'agriscore'")
    if cur.fetchone():
        print("User 'agriscore' already exists — updating password")
        cur.execute("ALTER USER agriscore WITH PASSWORD %s", (agriscore_password,))
    else:
        print("Creating user 'agriscore'")
        cur.execute("CREATE USER agriscore WITH PASSWORD %s", (agriscore_password,))

    # Create database if not exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'agriscore'")
    if cur.fetchone():
        print("Database 'agriscore' already exists")
    else:
        print("Creating database 'agriscore'")
        cur.execute("CREATE DATABASE agriscore OWNER agriscore")

    cur.close()
    conn.close()

    # Connect to agriscore database to enable PostGIS
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password=POSTGRES_PSSWD,
        dbname="agriscore",
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    print("PostGIS extension enabled")

    cur.execute("SELECT PostGIS_Version()")
    print(f"PostGIS version: {cur.fetchone()[0]}")

    # Grant privileges
    cur.execute("GRANT ALL PRIVILEGES ON DATABASE agriscore TO agriscore")
    cur.execute("GRANT ALL ON SCHEMA public TO agriscore")
    print("Privileges granted to 'agriscore'")

    cur.close()
    conn.close()

    # Build DATABASE_URL
    database_url = f"postgresql://agriscore:{agriscore_password}@localhost:5432/agriscore"

    # Update .env file
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path) as f:
            lines = [l for l in f.readlines() if not l.startswith("DATABASE_URL=")]

    lines.append(f"DATABASE_URL={database_url}\n")
    with open(env_path, "w") as f:
        f.writelines(lines)

    print("\nDATABASE_URL written to .env")
    print("Database setup complete!")


if __name__ == "__main__":
    main()
