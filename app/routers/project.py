from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ProjectResponse])
async def get_all_projects(db: AsyncSession = Depends(get_db)):
    return await ProjectService(db).get_all_projects()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    created_project = await service.create_project(project)
    return created_project


@router.get("/{name}", status_code=status.HTTP_200_OK, response_model=ProjectResponse)
async def get_project_by_name(name: str, db: AsyncSession = Depends(get_db)):
    service = ProjectService(db)
    project = await service.get_project_by_name(name)
    return project
