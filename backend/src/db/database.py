import asyncio
import json
import os
import time
from typing import AsyncGenerator, Optional
from urllib.parse import parse_qsl, urlencode
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/portfolio.db")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL") or DATABASE_URL

# RDS rotates its managed master password every 7 days. When this is set, the
# password is read from Secrets Manager whenever a connection is opened, and
# any password in DATABASE_URL is ignored.
DATABASE_PASSWORD_SECRET_ID = os.getenv("DATABASE_PASSWORD_SECRET_ID")
PASSWORD_CACHE_SECONDS = 60

_cached_password: Optional[tuple[float, str]] = None


def fetch_database_password() -> str:
    """Return the current database password from Secrets Manager.

    Cached briefly so a burst of new pool connections makes one API call.
    """
    global _cached_password
    now = time.monotonic()
    if _cached_password and now - _cached_password[0] < PASSWORD_CACHE_SECONDS:
        return _cached_password[1]

    import boto3

    client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION"))
    secret = client.get_secret_value(SecretId=DATABASE_PASSWORD_SECRET_ID)
    password = json.loads(secret["SecretString"])["password"]
    _cached_password = (now, password)
    return password


async def _fetch_database_password_async() -> str:
    # boto3 is blocking; keep the event loop free while it calls AWS.
    return await asyncio.to_thread(fetch_database_password)


def make_sync_database_url(database_url: str) -> str:
    """Convert async SQLAlchemy URLs to sync URLs for sync engines/migrations."""
    if database_url.startswith("postgresql+asyncpg://"):
        sync_url = database_url.replace(
            "postgresql+asyncpg://", "postgresql+psycopg://", 1
        )
        return _asyncpg_ssl_to_libpq(sync_url)
    if database_url.startswith("sqlite+aiosqlite://"):
        return database_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return database_url


def _asyncpg_ssl_to_libpq(database_url: str) -> str:
    """Rename asyncpg's ``ssl`` query option to psycopg/libpq's ``sslmode``.

    asyncpg rejects ``sslmode`` and psycopg rejects ``ssl``, so the same
    DATABASE_URL cannot serve both drivers without this translation. The URL
    is edited as text so an encoded password is left untouched.
    """
    base, sep, query = database_url.partition("?")
    if not sep:
        return database_url

    params = parse_qsl(query, keep_blank_values=True)
    translated = []
    for key, value in params:
        if key == "ssl":
            key = "sslmode"
            value = {"true": "require", "false": "disable"}.get(value.lower(), value)
        translated.append((key, value))
    return f"{base}?{urlencode(translated)}"


SYNC_DATABASE_URL = make_sync_database_url(DATABASE_URL)

# Determine if we're using SQLite or PostgreSQL
is_sqlite = "sqlite" in ASYNC_DATABASE_URL.lower()

# Configure connect_args based on database type
# SQLite-specific parameters should only be used with SQLite
async_connect_args = {}
sync_connect_args = {}
engine_kwargs = {
    "echo": os.getenv("DEBUG", "false").lower() == "true",
    "future": True,
    "pool_pre_ping": True,
    "pool_recycle": 300,  # Recycle connections every 5 minutes
}

if is_sqlite:
    async_connect_args = {"check_same_thread": False, "timeout": 30}
    sync_connect_args = {"check_same_thread": False, "timeout": 30}
    engine_kwargs["poolclass"] = StaticPool
elif DATABASE_PASSWORD_SECRET_ID:
    # asyncpg calls a password callable on every connection attempt.
    async_connect_args = {"password": _fetch_database_password_async}

# Create async engine with proper configuration
async_engine = create_async_engine(
    ASYNC_DATABASE_URL, connect_args=async_connect_args, **engine_kwargs
)

# Create sync engine for migrations and initial setup
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    connect_args=sync_connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Enable WAL mode for better concurrent access (SQLite only)
if is_sqlite:

    @event.listens_for(sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set SQLite pragmas for better performance and concurrent access."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
        cursor.close()


# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Sync session factory (for migrations and setup)
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


# Dependency to get async database session
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Async dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Dependency to get sync database session (for backwards compatibility)
def get_db():
    """Sync dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Database initialization
async def init_db() -> None:
    """Initialize missing tables for local/dev startup.

    Production schema changes should be managed with Alembic migrations, not
    ad-hoc create_all updates. This helper remains for backward compatibility
    and lightweight local development.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Database cleanup
async def close_db() -> None:
    """Close the database connection pool."""
    await async_engine.dispose()


# Health check function
async def check_db_health() -> bool:
    """Check database connectivity."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
