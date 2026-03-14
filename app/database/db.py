# app/database/db.py - Extended Async SQLAlchemy configuration
from functools import lru_cache
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from app.config.settings import get_settings
from app.utils.logging import logger
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from app.utils.db_utils import (
    calculate_pool_settings,
)


@lru_cache
def get_async_engine() -> AsyncEngine:
    """Create and cache a single AsyncEngine instance."""
    settings = get_settings()
    engine: AsyncEngine | None = None

    try:
        # Build the async database URL
        database_connection = URL.create(
            drivername="postgresql+asyncpg",
            username=settings.database.user,
            password=settings.database.password,
            host=settings.database.host,
            database="geovisor_db",
        )

        # Calculate pool settings dynamically based on expected load
        pool_config = calculate_pool_settings(
            expected_concurrent_requests=200,  # example: adjust to your traffic
            db_max_connections=100,  # PostgreSQL max connections
        )

        # Create the async engine
        engine = create_async_engine(
            database_connection,
            # Connection pool configuration
            pool_size=pool_config["pool_size"],  # Permanent connections in pool
            max_overflow=pool_config[
                "max_overflow"
            ],  # Temporary connections during spikes
            pool_timeout=pool_config["pool_timeout"],  # Wait time for connection
            pool_recycle=pool_config["pool_recycle"],  # Prevent stale connections
            pool_pre_ping=True,  # Verify connection before use
            # SQL logging for debugging
            echo=False,  # Change to True to debug queries
        )
    except SQLAlchemyError:
        logger.exception("Failed to create async engine")

    return engine


# Create async session factory
async_session_factory = async_sessionmaker(
    get_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep data accessible after commit
    autocommit=False,  # Require explicit commits
    autoflush=False,  # Manual control over flushing
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session for each request.

    The session is automatically closed when the request completes,
    even if an exception occurs. This prevents connection leaks.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            # Rollback on any exception to maintain data integrity
            await session.rollback()
            raise
        finally:
            # Session is automatically closed by the context manager
            pass


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass
