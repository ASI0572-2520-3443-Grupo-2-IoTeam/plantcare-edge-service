import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL")

if not DATABASE_URL:
    DATABASE_URL = (
        "mysql://root:RXXtpcEhPqTRhqzOuXvWQCedlaVWTjIn@maglev.proxy.rlwy.net:29969/railway"
    )

if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)


try:
    import pymysql

    pymysql.install_as_MySQLdb()
except Exception:
 
    pass




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


try:
    masked = re.sub(r":[^@]+@", ":****@", DATABASE_URL)
except Exception:
    masked = DATABASE_URL

print("[shared.database] DATABASE_URL=", masked)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
 
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
