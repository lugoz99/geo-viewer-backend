import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database.db import get_db
from app.config.settings import get_settings


# 👇 Engine separado para tests (evita conflictos con el engine global)
@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        get_settings().asyncpg_url.unicode_string(),
        echo=False,  # Desactiva logs para tests
        pool_size=1,  # Una sola conexión
        max_overflow=0,  # No crear conexiones adicionales
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session_factory(test_engine):
    """Factory para crear sesiones de test"""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest.fixture
async def async_client(test_session_factory):
    """Cliente HTTP para tests con BD override"""

    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
