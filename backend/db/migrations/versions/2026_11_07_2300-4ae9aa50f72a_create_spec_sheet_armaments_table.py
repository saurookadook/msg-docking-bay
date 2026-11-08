"""Create spec_sheet_armaments table.

Revision ID: 4ae9aa50f72a
Revises: 63fa030fbc2e
Create Date: 2026-11-07 22:59:52.846806+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import create_pg_enum, drop_pg_enum

revision: str = "4ae9aa50f72a"
down_revision: str | Sequence[str] | None = "63fa030fbc2e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ARMAMENT_MOUNT_VALUES = [
    "fixed",
    "handheld",
    "optional_fixed",
    "optional_handheld",
]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop it (ALEM-11).
    armament_mount = create_pg_enum("armament_mount", ARMAMENT_MOUNT_VALUES)
    # A junction table keyed on (armament, mount, sheet), with no
    # surrogate ``id`` (RDB-2). No ``source_id``: the sheet's source
    # covers its parts. RESTRICT on the armament keeps a listed part.
    op.create_table(
        "spec_sheet_armaments",
        sa.Column("armament_id", sa.Uuid(), nullable=False),
        sa.Column("mount", armament_mount, nullable=False),
        sa.Column("note", sa.TEXT(), nullable=True),
        sa.Column("quantity_max", sa.Integer(), nullable=True),
        sa.Column("quantity_min", sa.Integer(), nullable=True),
        sa.Column("spec_sheet_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(note) > 0", name=op.f("ck_spec_sheet_armaments_note_not_empty")
        ),
        sa.CheckConstraint(
            "quantity_max >= quantity_min",
            name=op.f("ck_spec_sheet_armaments_quantities_in_order"),
        ),
        sa.CheckConstraint(
            "quantity_max IS NULL OR quantity_min IS NOT NULL",
            name=op.f("ck_spec_sheet_armaments_quantity_max_needs_quantity_min"),
        ),
        sa.CheckConstraint(
            "quantity_min > 0",
            name=op.f("ck_spec_sheet_armaments_quantity_min_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["armament_id"],
            ["armaments.id"],
            name=op.f("spec_sheet_armaments_armament_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["spec_sheet_id"],
            ["spec_sheets.id"],
            name=op.f("spec_sheet_armaments_spec_sheet_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "armament_id",
            "mount",
            "spec_sheet_id",
            name=op.f("spec_sheet_armaments_pkey"),
        ),
    )
    op.create_index(
        op.f("ix_spec_sheet_armaments_spec_sheet_id"),
        "spec_sheet_armaments",
        ["spec_sheet_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_spec_sheet_armaments_spec_sheet_id"), table_name="spec_sheet_armaments"
    )
    op.drop_table("spec_sheet_armaments")
    drop_pg_enum("armament_mount", ARMAMENT_MOUNT_VALUES)
