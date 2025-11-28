import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

"""
Database Configuration

This module sets up the database connection for the application. It uses SQLAlchemy to manage the connection and sessions.

Configuration:
- The database connection URL is constructed using environment variables.
- Defaults are provided for local development (MySQL).

Environment Variables:
- DB_USER: The username for the database (default: 'root').
- DB_PASSWORD: The password for the database (default: 'root').
- DB_HOST: The hostname of the database server (default: 'localhost').
- DB_PORT: The port number for the database server (default: '3306').
- DB_NAME: The name of the database (default: 'plant_database').

Functions:
- get_db_session: Provides a database session for use in the application.
"""

# --- Configuración de la Base de Datos ---

# Priority order for the connection URL:
# 1. Full DATABASE_URL or DB_URL environment variable (if set)
# 2. Construct from individual MYSQL_* environment variables (Railway standard)
# 3. Fallback to local MySQL defaults

# Option 1: Use full DATABASE_URL if provided
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL")

# Option 2: If not provided, construct from individual Railway env vars
if not DATABASE_URL:
    mysql_user = os.getenv("MYSQL_USER") or os.getenv("MYSQLUSER", "root")
    mysql_password = os.getenv("MYSQL_ROOT_PASSWORD") or os.getenv("MYSQLPASSWORD", "root")
    mysql_host = os.getenv("MYSQL_PUBLIC_HOST", os.getenv("MYSQLHOST", "localhost"))
    mysql_port = os.getenv("MYSQL_PUBLIC_PORT", os.getenv("MYSQLPORT", "3306"))
    mysql_database = os.getenv("MYSQL_DATABASE") or os.getenv("MYSQLDATABASE", "railway")
    
    # Construct the URL
    DATABASE_URL = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

# Normalize URL: if someone provided a plain `mysql://` scheme, prefer `pymysql`.
# This ensures SQLAlchemy uses the pure-Python `pymysql` driver instead of
# attempting to import `MySQLdb` (which requires `mysqlclient`/MySQLdb C extension).
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Some environments or libraries may still try to import `MySQLdb` directly.
# If `pymysql` is available, install it as a drop-in replacement for `MySQLdb`.
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except Exception:
    # If pymysql isn't installed, the import will fail. The app should have
    # `pymysql` in `requirements.txt` for the remote deploy. We'll continue
    # and let SQLAlchemy raise a clear error if the driver is missing.
    pass



# Enable SQLAlchemy echo to log SQL statements for debugging and
# print the DATABASE_URL so we can confirm which database is being used.
# Connection options to improve resilience on unstable networked DBs
ECHO_SQL = os.getenv("DB_ECHO", "false").lower() == "true"
POOL_PRE_PING = True
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))
CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "30"))

engine = create_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    pool_pre_ping=POOL_PRE_PING,
    pool_recycle=POOL_RECYCLE,
    connect_args={"connect_timeout": CONNECT_TIMEOUT},
)

# Print a masked DATABASE_URL (hide password) for debugging without leaking secrets
try:
    masked = re.sub(r":[^@]+@", ":****@", DATABASE_URL)
except Exception:
    masked = DATABASE_URL

print("[shared.database] DATABASE_URL=", masked)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
    """
    Provides a database session to the application.

    This function creates a new SQLAlchemy session bound to the database engine.
    The session is used to interact with the database and is automatically closed
    after use.

    Yields:
        Session: A SQLAlchemy session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
