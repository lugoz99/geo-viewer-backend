from app.schemas.custom_base import CustomBase


import uuid


class UserCreate(CustomBase):
    email: str
    full_name: str
    company_name: str
    hashed_password: str
    is_active: bool = True
    photo_url: str | None = None
    role: str = "user"


class UserUpdate(CustomBase):
    """Schema para actualizar usuario (todos los campos opcionales)"""

    email: str | None = None
    full_name: str | None = None
    company_name: str | None = None
    is_active: bool | None = None
    photo_url: str | None = None
    role: str | None = None


class UserResponse(CustomBase):
    id: uuid.UUID
    email: str
    full_name: str
    company_name: str
    is_active: bool
    photo_url: str | None = None
    role: str
