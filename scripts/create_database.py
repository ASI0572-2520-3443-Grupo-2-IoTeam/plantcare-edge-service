"""Create database if missing and run SQLAlchemy metadata.create_all.

Usage:
  Set `DATABASE_URL` or `DB_URL` environment variable (same format as in
  `shared/database.py`). Then run:

    python scripts/create_database.py

This script will:
  - Parse the DB URL to obtain host/user/port/password and database name.
  - Connect to the MySQL server (without selecting a database) and run
    `CREATE DATABASE IF NOT EXISTS <db>` with utf8mb4 charset.
  - Call `Base.metadata.create_all(bind=engine)` to create tables.

Be careful not to run this in production repeatedly; prefer a migration tool
for managed schema changes.
"""
import os
import sys
import traceback

try:
    from sqlalchemy.engine.url import make_url
except Exception:
    # SQLAlchemy backwards compat
    from sqlalchemy.engine import make_url

try:
    import pymysql
except Exception:
    print("Missing dependency: install 'pymysql' first (pip install pymysql)")
    sys.exit(1)


def main():
    DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if not DATABASE_URL:
        print("No DATABASE_URL or DB_URL environment variable found.")
        sys.exit(1)

    # Normalize plain mysql:// to mysql+pymysql:// just like shared.database
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

    url = make_url(DATABASE_URL)
    db_name = url.database
    if not db_name:
        print("The provided DATABASE_URL does not include a database name.")
        sys.exit(1)

    host = url.host or "localhost"
    port = url.port or 3306
    user = url.username or "root"
    password = url.password or ""

    print(f"Connecting to MySQL server at {host}:{port} as {user} to create '{db_name}'...")

    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
                )
            conn.commit()
            print(f"Database '{db_name}' ensured (created if it did not exist).")
        finally:
            conn.close()
    except Exception:
        print("Failed to create database. See traceback:")
        traceback.print_exc()
        sys.exit(1)

    # Now create tables using SQLAlchemy metadata
    try:
        # Import here to reuse shared engine and model Base
        from shared.database import engine
        from plant.infrastructure.models import Base

        print("Creating tables from metadata...")
        Base.metadata.create_all(bind=engine)
        print("Tables created (or already present).")
    except Exception:
        print("Failed to create tables. See traceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
