import os
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

# --- Configuración de la Base de Datos lista para Producción ---

# Usar configuración local por defecto
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "plantabase")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Enable SQLAlchemy echo to log SQL statements for debugging and
# print the DATABASE_URL so we can confirm which database is being used.
engine = create_engine(DATABASE_URL, echo=True)

print("[shared.database] DATABASE_URL=", DATABASE_URL)
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
