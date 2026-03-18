import enum
from app.database.db import Base
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import  UUID
import uuid

if TYPE_CHECKING:
    from app.models import User
    from app.models import Layer


class ProjectStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique identifier for the feature.",
    )
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.ACTIVE
    )
    # relationships
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    layers: Mapped[list["Layer"]] = relationship("Layer", back_populates="project")
