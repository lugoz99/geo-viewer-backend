"""create file_imports table

Revision ID: a1b2c3d4e5f6
Revises: f2b9ac039ca0
Create Date: 2026-05-02

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f2b9ac039ca0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear enum para ImportStatus como string (native_enum=False)
    op.create_table(
        "file_imports",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            primary_key=True,
        ),
        # ── Relaciones ────────────────────────────────────────
        sa.Column(
            "project_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "layer_id",
            sa.UUID(),
            nullable=True,
        ),
        # ── Estado ────────────────────────────────────────────
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            default="pending",
        ),
        sa.Column(
            "progress",
            sa.Integer(),
            nullable=False,
            default=0,
            comment="Progress percentage (0-100)",
        ),
        # ── Info del archivo ─────────────────────────────────
        sa.Column(
            "file_name",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "file_type",
            sa.String(50),
            nullable=False,
            comment="geojson, kml, csv, excel, etc.",
        ),
        # ── Análisis y mapping ───────────────────────────────
        sa.Column(
            "analysis",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Raw analysis result: detected columns, sheets, folders, geometry types, auto-mapping suggestions.",
        ),
        sa.Column(
            "column_mapping",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="User-confirmed column mapping (lat, lon, attributes). NULL for auto-import formats.",
        ),
        sa.Column(
            "created_layer_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="List of UUIDs of layers created by this import. Supports multi-layer imports.",
        ),
        # ── Resultados ───────────────────────────────────────
        sa.Column(
            "total_rows",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "features_imported",
            sa.Integer(),
            nullable=False,
            default=0,
        ),
        sa.Column(
            "features_failed",
            sa.Integer(),
            nullable=False,
            default=0,
        ),
        sa.Column(
            "error_log",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Errors per row (limited size recommended)",
        ),
        # ── Tiempos ──────────────────────────────────────────
        sa.Column(
            "started_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "finished_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Timestamp when the record was created.",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Timestamp of the last modification.",
        ),
        # ── Foreign Keys ─────────────────────────────────────
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["layer_id"],
            ["layers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("file_imports")
