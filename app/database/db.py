import datetime
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy import DateTime, pool
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
    AsyncAttrs,
)
from app.config.settings import get_settings as global_settings
from app.utils.logging import logger
from fastapi.exceptions import ResponseValidationError

# ─── Engine ───────────────────────────────────────────────
# We save the engine here so we don't create it every time
engine = create_async_engine(
    global_settings().asyncpg_url.unicode_string(),
    future=True,
    echo=True,
)


AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)

# def get_async_engine() -> AsyncEngine:
#     """Returns the engine. Creates it only once (first call)."""
#     global _engine_instance

#     if _engine_instance is None:
#         settings = get_settings()
#         try:
#             _engine_instance = create_async_engine(
#                 str(settings.asyncpg_url),  # database URL
#                 poolclass=pool.NullPool,  # no connection pool
#                 echo=False,  # set True to see SQL queries
#             )
#             logger.info("Async engine created successfully")
#         except SQLAlchemyError:
#             logger.exception("Failed to create async engine")
#             raise

#     return _engine_instance


# def reset_engine() -> None:
#     """Delete the engine. Useful for tests."""
#     global _engine_instance
#     if _engine_instance:
#         logger.info("Engine reset")
#         _engine_instance = None


# # ─── Session factory ──────────────────────────────────────
# def get_session_factory() -> async_sessionmaker[AsyncSession]:
#     """Creates a new session factory using the current engine."""
#     return async_sessionmaker(
#         get_async_engine(),
#         class_=AsyncSession,
#         expire_on_commit=False,  # keep data after commit
#         autocommit=False,  # we commit manually
#         autoflush=False,  # we flush manually
#     )


# ─── Session ──────────────────────────────────────────────
@asynccontextmanager
# Dependency
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            # Re-raise SQLAlchemy errors to be handled by the global handler
            raise
        except Exception as ex:
            # Only log actual database-related issues, not response validation
            if not isinstance(ex, ResponseValidationError):
                await logger.aerror(f"Database-related error: {repr(ex)}")
            raise  # Re-raise to be handled by appropriate handlers


# ─── Base model ───────────────────────────────────────────
class Base(AsyncAttrs, DeclarativeBase):
    """All models inherit from this class."""

    # Use timezone-aware datetime for all datetime columns
    type_annotation_map = {
        datetime.datetime: DateTime(timezone=True),
    }
