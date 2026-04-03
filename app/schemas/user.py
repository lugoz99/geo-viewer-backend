from app.schemas.custom_base import CustomBase


import uuid


# Data that user sends to create new user
class UserCreate(CustomBase):
    """Information needed to make a new user"""

    email: str
    full_name: str
    company_name: str
    hashed_password: str
    is_active: bool = True
    photo_url: str | None = None
    role: str = "user"


# Data that user sends to change user information
class UserUpdate(CustomBase):
    """Information to change about a user (all fields are optional)"""

    email: str | None = None
    full_name: str | None = None
    company_name: str | None = None
    is_active: bool | None = None
    photo_url: str | None = None
    role: str | None = None


# Data that API sends back to user
class UserResponse(CustomBase):
    """User data that API shows to client"""

    id: uuid.UUID
    email: str
    full_name: str
    company_name: str
    is_active: bool
    photo_url: str | None = None
    role: str
