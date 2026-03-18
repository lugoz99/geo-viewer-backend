import asyncio
import sys
import logging
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from rich.logging import RichHandler

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database.db import Base
from app.config.settings import get_settings
from app.models import *  # noqa: F403 - force model registration

# ─── Alembic config ───────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Setup rich logging AFTER fileConfig so it doesn't get overwritten
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    force=True,
)

# ─── Get URL from settings ────────────────────────────────
settings = get_settings()
url = settings.asyncpg_url.unicode_string()
config.set_main_option("sqlalchemy.url", url)

target_metadata = Base.metadata


# ─── Ignore PostGIS tables ────────────────────────────────
def include_object(object, name, type_, reflected, compare_to):
    """Ignore PostGIS system tables."""
    if type_ == "table" and name in ("spatial_ref_sys", "topology", "layer"):
        return False
    return True


# ─── Offline migrations ───────────────────────────────────
def run_migrations_offline() -> None:
    """Run migrations without a live DB connection."""
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


# ─── Online migrations ────────────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create async engine and run migrations."""
    connectable = create_async_engine(url, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ─── Entry point ──────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
