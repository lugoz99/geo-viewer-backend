import uuid
from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
import enum
from geoalchemy2 import Geometry
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models import Layer


class FeatureStatus(enum.Enum):
    ACTIVE = "active"
    DELETED = "deleted"


class Feature(Base):
    __tablename__ = "features"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique identifier for the feature.",
    )

    geom: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
        nullable=False,
        comment="Native PostGIS geometry in WGS84.",
    )
    attributes: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Feature attributes as key-value pairs. Flexible schema per layer.",
    )
    status: Mapped[FeatureStatus] = mapped_column(
        Enum(FeatureStatus, name="feature_status_enum"),
        default=FeatureStatus.ACTIVE,
        nullable=False,
        comment="Logical delete flag.",
    )

    # ── Relationships ─────────────────────────────────────────
    layer: Mapped["Layer"] = relationship("Layer", back_populates="features")
    layer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("layers.id", ondelete="CASCADE"),
        nullable=False,
        comment="Layer this feature belongs to.",
    )
