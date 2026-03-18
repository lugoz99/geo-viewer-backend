import enum
from sqlalchemy import Enum, func  
from app.database.db import Base
from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

# For type hinting to avoid circular imports
if TYPE_CHECKING:
    from app.models import Project


# Role Enum
class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique identifier for the feature.",
    )
    email: Mapped[str] = mapped_column(unique=True)
    full_name: Mapped[str]
    company_name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    hashed_password: Mapped[str]
    photo_url: Mapped[Optional[str]] = mapped_column(default=None)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    # Relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")
