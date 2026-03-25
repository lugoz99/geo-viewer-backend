from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
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
    echo=False,
)

# ?: ¿COMO OPTIMIZAR LOS POOL DE CONTEXIONES?
AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            # Provide DB session to request lifecycle
            yield session

        except Exception:
            # Rollback any failed transaction
            await session.rollback()
            raise

        # session is auto-closed by async with


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models. Provides created_at and updated_at timestamps."""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), comment="Timestamp when the record was created."
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp of the last modification.",
    )
