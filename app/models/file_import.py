import enum
import uuid
from sqlalchemy import String, Integer, Enum as SqlEnum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database.db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import User
    from app.models import Project


class ImportStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    NEEDS_MAPPING = "needs_mapping"
    COMPLETED = "completed"
    FAILED = "failed"


class FileImport(Base):
    __tablename__ = "file_imports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Relaciones ────────────────────────────────────────────
    # FK al proyecto donde se importa el archivo (se necesita antes de crear el layer)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
    )

    # FK al usuario que subió el archivo
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # FK al layer creado (NULL hasta que se ejecute la importación)
    layer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("layers.id"),
        nullable=True,
    )

    # ── Relationships para navegación ─────────────────────────
    # Permite acceder a import.project sin join manual
    project: Mapped["Project"] = relationship("Project", back_populates="imports")
    user: Mapped["User"] = relationship("User")

    # ── Estado del proceso ───────────────────────────────────
    status: Mapped[ImportStatus] = mapped_column(
        SqlEnum(
            ImportStatus,
            name="importstatus",
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
        ),
        default=ImportStatus.PENDING,
        nullable=False,
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Progress percentage (0-100)",
    )

    # ── Info del archivo ─────────────────────────────────────
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="geojson, kml, csv, excel, etc.",
    )

    # ── Análisis inicial del archivo ─────────────────────────
    # Guarda el resultado crudo del análisis: columnas detectadas,
    # sheets (Excel), folders (KML), tipos de geometría encontrados,
    # sugerencias de mapeo auto-detectadas. Se llena en /upload.
    analysis: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Raw analysis result: detected columns, sheets, folders, geometry types, auto-mapping suggestions.",
    )

    # ── Mapping confirmado por el usuario (CSV/Excel) ────────
    # Mapeo final que el usuario confirma: qué columna es lat, lon,
    # qué columnas van a attributes, etc. NULL para GeoJSON/KML auto.
    column_mapping: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="User-confirmed column mapping (lat, lon, attributes). NULL for auto-import formats.",
    )

    # ── IDs de layers creados ─────────────────────────────────
    # Para imports que crean múltiples layers (KML con folders,
    # Excel con sheets). Para imports simples, solo tiene 1 ID.
    created_layer_ids: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of UUIDs of layers created by this import. Supports multi-layer imports.",
    )

    # ── Resultados ───────────────────────────────────────────
    total_rows: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    features_imported: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    features_failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_log: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Errors per row (limited size recommended)",
    )

    # ── Tiempos ──────────────────────────────────────────────
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
