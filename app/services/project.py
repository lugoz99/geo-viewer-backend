from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.exceptions.request_exception import NotFoundError
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate


class ProjectService:
    """Service to manage projects in database"""

    def __init__(self, db: AsyncSession):
        # db: connection to database
        self.db = db

    async def get_all_projects(self) -> list[Project]:
        return await self.db.scalars(select(Project).where(Project.is_active)).all()

    async def create_project(self, project_schema: ProjectCreate) -> Project:

        owner_db = await self.db.get(User, project_schema.owner_id)
        if not owner_db:
            raise NotFoundError("Owner not found")

        new_project = Project(**project_schema.model_dump())
        self.db.add(new_project)
        try:
            # Save to database
            await self.db.commit()
            # Refresh to get generated values (like id)
            await self.db.refresh(new_project)
            return new_project

        except SQLAlchemyError:
            # If error, undo changes
            await self.db.rollback()
            raise

    async def get_project_by_name(self, name: str) -> Project:
        result = await self.db.scalar(
            select(Project)
            .options(joinedload(Project.owner))
            .where(Project.name == name)
        )
        if not result:
            raise NotFoundError("Project not found")
        return result

    async def disable_project(self, project_id: int) -> None:
        project = await self.db.get(Project, project_id)
        if not project:
            raise NotFoundError("Project not found")
        project.is_active = False
        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
