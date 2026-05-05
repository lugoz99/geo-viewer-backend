import uuid
from sqlalchemy import select
from app.models import Project, User
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.request_exception import NotFoundError
from app.models.project import ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service to manage projects in database"""

    def __init__(self, db: AsyncSession):
        # db: connection to database
        self.db = db

    async def get_all_projects(self) -> list[Project]:
        # scalar result -> it returns only the Project objects, without metadata
        stmt = (
            select(Project)
            .where(Project.status == ProjectStatus.ACTIVE)
            .options(joinedload(Project.owner))
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

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

    async def update_one_project(
        self, id: uuid.UUID, project_schema: ProjectUpdate
    ) -> Project:

        project_db = await self.db.get(Project, id)
        if not project_db:
            raise NotFoundError("Project not found")

        # Update only provided fields, exclude unset fields,
        # because we don't want to overwrite existing values with None
        update_project = project_schema.model_dump(exclude_unset=True)
        for key, value in update_project.items():
            # Set new value to project_db, for example project_db.name = update_project.name
            setattr(project_db, key, value)

        try:
            # Save to database
            await self.db.commit()
            # Refresh to get generated values (like id)
            await self.db.refresh(project_db)
            return project_db

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

    async def disable_project(self, project_id: uuid.UUID) -> None:
        project = await self.db.get(Project, project_id)
        if not project:
            raise NotFoundError("Project not found")
        project.status = ProjectStatus.INACTIVE
        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
