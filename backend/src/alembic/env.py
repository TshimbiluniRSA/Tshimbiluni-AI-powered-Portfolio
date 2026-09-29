"""Alembic environment configuration for portfolio backend migrations."""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, make_url, pool

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db.database import (  # noqa: E402
    DATABASE_PASSWORD_SECRET_ID,
    Base,
    fetch_database_password,
    make_sync_database_url,
)
from db import models  # noqa: F401,E402 - import models so metadata is populated

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url():
    """Return a synchronous SQLAlchemy URL for Alembic migrations."""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/portfolio.db")
    url = make_url(make_sync_database_url(database_url))

    if DATABASE_PASSWORD_SECRET_ID and not url.drivername.startswith("sqlite"):
        url = url.set(password=fetch_database_password())

    return url


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    connectable = create_engine(get_database_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
