import enum
import uuid
from sqlalchemy import String, Integer, Text, Enum as SqlEnum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database.db import Base


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

    # ── Relación ─────────────────────────────────────────────
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    layer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("layers.id"),
        nullable=True,
    )

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

    # ── Mapping dinámico (CSV/Excel) ─────────────────────────
    column_mapping: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="User-defined mapping for columns (lat, lon, etc.)",
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
