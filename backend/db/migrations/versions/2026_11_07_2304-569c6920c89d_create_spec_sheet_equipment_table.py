"""Create spec_sheet_equipment table.

Revision ID: 569c6920c89d
Revises: fb0daabb5e11
Create Date: 2026-11-07 23:04:03.477199+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import create_pg_enum, drop_pg_enum

revision: str = "569c6920c89d"
down_revision: str | Sequence[str] | None = "fb0daabb5e11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EQUIPMENT_FIT_VALUES = [
    "standard",
    "optional",
]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop it (ALEM-11).
    equipment_fit = create_pg_enum("equipment_fit", EQUIPMENT_FIT_VALUES)
    # A junction table keyed on (equipment, fit, sheet), with no
    # surrogate ``id`` (RDB-2). No ``source_id``: the sheet's source
    # covers its parts. RESTRICT on the part keeps a listed one.
    op.create_table(
        "spec_sheet_equipment",
        sa.Column("equipment_id", sa.Uuid(), nullable=False),
        sa.Column("fit", equipment_fit, nullable=False),
        sa.Column("note", sa.TEXT(), nullable=True),
        sa.Column("spec_sheet_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(note) > 0", name=op.f("ck_spec_sheet_equipment_note_not_empty")
        ),
        sa.ForeignKeyConstraint(
            ["equipment_id"],
            ["equipment.id"],
            name=op.f("spec_sheet_equipment_equipment_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["spec_sheet_id"],
            ["spec_sheets.id"],
            name=op.f("spec_sheet_equipment_spec_sheet_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "equipment_id",
            "fit",
            "spec_sheet_id",
            name=op.f("spec_sheet_equipment_pkey"),
        ),
    )
    op.create_index(
        op.f("ix_spec_sheet_equipment_spec_sheet_id"),
        "spec_sheet_equipment",
        ["spec_sheet_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_spec_sheet_equipment_spec_sheet_id"), table_name="spec_sheet_equipment"
    )
    op.drop_table("spec_sheet_equipment")
    drop_pg_enum("equipment_fit", EQUIPMENT_FIT_VALUES)
