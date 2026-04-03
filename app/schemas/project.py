import uuid
from app.schemas.custom_base import CustomBase
from app.schemas.user import UserResponse


class ProjectCreate(CustomBase):
    name: str
    description: str | None = None
    status: str = "active"
    owner_id: uuid.UUID


class ProjectUpdate(CustomBase):
    """Schema para actualizar proyecto (todos los campos opcionales)"""

    name: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectResponse(CustomBase):
    id: uuid.UUID
    name: str
    description: str | None = None
    status: str
    owner_id: uuid.UUID
    owner: UserResponse
