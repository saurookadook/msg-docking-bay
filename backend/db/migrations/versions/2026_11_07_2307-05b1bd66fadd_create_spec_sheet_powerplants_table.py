"""Create spec_sheet_powerplants table.

Revision ID: 05b1bd66fadd
Revises: 351ca28410b5
Create Date: 2026-11-07 23:06:19.465495+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "05b1bd66fadd"
down_revision: str | Sequence[str] | None = "351ca28410b5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # A junction table keyed on (powerplant, sheet), with no
    # surrogate ``id`` (RDB-2). No ``source_id``: the sheet's source
    # covers its parts. RESTRICT on the part keeps a listed one.
    op.create_table(
        "spec_sheet_powerplants",
        sa.Column("note", sa.TEXT(), nullable=True),
        sa.Column("powerplant_id", sa.Uuid(), nullable=False),
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
            "char_length(note) > 0",
            name=op.f("ck_spec_sheet_powerplants_note_not_empty"),
        ),
        sa.CheckConstraint(
            "quantity_max >= quantity_min",
            name=op.f("ck_spec_sheet_powerplants_quantities_in_order"),
        ),
        sa.CheckConstraint(
            "quantity_max IS NULL OR quantity_min IS NOT NULL",
            name=op.f("ck_spec_sheet_powerplants_quantity_max_needs_min"),
        ),
        sa.CheckConstraint(
            "quantity_min > 0",
            name=op.f("ck_spec_sheet_powerplants_quantity_min_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["powerplant_id"],
            ["powerplants.id"],
            name=op.f("spec_sheet_powerplants_powerplant_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["spec_sheet_id"],
            ["spec_sheets.id"],
            name=op.f("spec_sheet_powerplants_spec_sheet_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "powerplant_id", "spec_sheet_id", name=op.f("spec_sheet_powerplants_pkey")
        ),
    )
    op.create_index(
        op.f("ix_spec_sheet_powerplants_spec_sheet_id"),
        "spec_sheet_powerplants",
        ["spec_sheet_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_spec_sheet_powerplants_spec_sheet_id"),
        table_name="spec_sheet_powerplants",
    )
    op.drop_table("spec_sheet_powerplants")
