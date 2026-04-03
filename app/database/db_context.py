# app/database/db_context.py
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import async_session_factory


@asynccontextmanager
async def get_db_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for use outside of FastAPI requests.

    Useful for:
    - Background tasks (cron jobs, Celery tasks, periodic jobs)
    - CLI commands or scripts
    - Tests (unit or integration tests)

    Features:
    - Provides an AsyncSession instance
    - Commits automatically if no exceptions occur
    - Rolls back automatically if an exception happens
    - Ensures session is closed properly to prevent connection leaks
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()  # Commit changes after successful execution
        except Exception:
            await session.rollback()  # Rollback on error to maintain data integrity
            raise


# import asyncio
# from app.database.db_context import get_db_session_context
# from app.models.project import Project

# async def main():
#     async with get_db_session_context() as session:
#         new_project = Project(name="GeoApp", description="Geo Viewer")
#         session.add(new_project)
#         print("Project added successfully!")

# if __name__ == "__main__":
#     asyncio.run(main())
