import os
from typing import AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
load_dotenv()

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/portfolio.db")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL") or DATABASE_URL

# Determine if we're using SQLite or PostgreSQL
is_sqlite = "sqlite" in ASYNC_DATABASE_URL.lower()

# Configure connect_args based on database type
# SQLite-specific parameters should only be used with SQLite
async_connect_args = {}
sync_connect_args = {}

if is_sqlite:
    async_connect_args = {"check_same_thread": False, "timeout": 30}
    sync_connect_args = {"check_same_thread": False, "timeout": 30}

# Create async engine with proper configuration
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    future=True,
    connect_args=async_connect_args,
    poolclass=StaticPool if is_sqlite else None,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections every 5 minutes
)

# Create sync engine for migrations and initial setup
sync_engine = create_engine(
    DATABASE_URL,
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
    """ Sync dependency to get database session. """
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
    """Initialize the database by creating all tables."""
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
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False