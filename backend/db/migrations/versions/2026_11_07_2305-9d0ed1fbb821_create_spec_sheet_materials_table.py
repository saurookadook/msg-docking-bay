"""Create spec_sheet_materials table.

Revision ID: 9d0ed1fbb821
Revises: 4616250031f0
Create Date: 2026-11-07 23:05:18.928823+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import create_pg_enum, drop_pg_enum

revision: str = "9d0ed1fbb821"
down_revision: str | Sequence[str] | None = "4616250031f0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MATERIAL_USE_VALUES = [
    "armor",
    "frame",
]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop it (ALEM-11).
    material_use = create_pg_enum("material_use", MATERIAL_USE_VALUES)
    # A junction table keyed on (material, use, sheet), with no
    # surrogate ``id`` (RDB-2). No ``source_id``: the sheet's source
    # covers its parts. RESTRICT on the part keeps a listed one.
    op.create_table(
        "spec_sheet_materials",
        sa.Column("material_id", sa.Uuid(), nullable=False),
        sa.Column("material_use", material_use, nullable=False),
        sa.Column("note", sa.TEXT(), nullable=True),
        sa.Column("spec_sheet_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(note) > 0", name=op.f("ck_spec_sheet_materials_note_not_empty")
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["materials.id"],
            name=op.f("spec_sheet_materials_material_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["spec_sheet_id"],
            ["spec_sheets.id"],
            name=op.f("spec_sheet_materials_spec_sheet_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "material_id",
            "material_use",
            "spec_sheet_id",
            name=op.f("spec_sheet_materials_pkey"),
        ),
    )
    op.create_index(
        op.f("ix_spec_sheet_materials_spec_sheet_id"),
        "spec_sheet_materials",
        ["spec_sheet_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_spec_sheet_materials_spec_sheet_id"), table_name="spec_sheet_materials"
    )
    op.drop_table("spec_sheet_materials")
    drop_pg_enum("material_use", MATERIAL_USE_VALUES)
