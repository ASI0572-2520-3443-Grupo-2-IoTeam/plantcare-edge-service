import os
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

try:
    from sqlalchemy.engine.url import make_url
except ImportError:
    from sqlalchemy.engine import make_url


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


def ensure_database_exists():
    """
    Creates the database if it doesn't exist.
    Connects to MySQL server without specifying a database, then runs CREATE DATABASE IF NOT EXISTS.
    """
    try:
        url = make_url(DATABASE_URL)
        db_name = url.database
        
        if not db_name:
            print("[shared.database] No database name in URL, skipping database creation")
            return
        
        # Create connection URL without database name
        server_url = url.set(database=None)
        
        # Connect to server (without selecting a database) - no timeouts for persistent connection
        temp_engine = create_engine(
            server_url,
            connect_args={
                "charset": "utf8mb4",
            },
        )
        
        with temp_engine.connect() as conn:
            # Use raw connection to execute CREATE DATABASE
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"))
            conn.commit()
        
        temp_engine.dispose()
        print(f"[shared.database] Database '{db_name}' ensured (created if it did not exist)")
        
    except Exception as e:
        print(f"[shared.database] Warning: Could not ensure database exists: {e}")
        print("[shared.database] Continuing anyway - database may already exist")




ECHO_SQL = os.getenv("DB_ECHO", "false").lower() == "true"

# Connection tuning: prefer verifying connections before use and
# recycle them periodically to avoid using stale sockets behind proxies.
POOL_PRE_PING = True
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "300"))  # 5 minutes
CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "30"))
READ_TIMEOUT = int(os.getenv("DB_READ_TIMEOUT", "60"))
WRITE_TIMEOUT = int(os.getenv("DB_WRITE_TIMEOUT", "60"))

engine = create_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    pool_pre_ping=POOL_PRE_PING,
    pool_recycle=POOL_RECYCLE,
    pool_size=20,  # Increase from default 5 to handle more concurrent requests
    max_overflow=30,  # Increase from default 10 to allow more overflow connections
    pool_timeout=30,  # Wait up to 30 seconds for a connection
    connect_args={
        "connect_timeout": CONNECT_TIMEOUT,
        "read_timeout": READ_TIMEOUT,
        "write_timeout": WRITE_TIMEOUT,
        "charset": "utf8mb4",
    },
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
