"""Create character_appearances table.

Revision ID: 21f9f46a85ea
Revises: 2102b73c0dd8
Create Date: 2026-11-08 02:46:09.091258+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "21f9f46a85ea"
down_revision: str | Sequence[str] | None = "2102b73c0dd8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # A junction table keyed on (character, work), with no surrogate
    # ``id`` (RDB-2). ``character_id`` leads the key, so only
    # ``work_id`` and ``source_id`` need indexes (RDB-18).
    op.create_table(
        "character_appearances",
        sa.Column("character_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("work_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # CASCADE on character and work: an appearance needs both.
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
            name=op.f("character_appearances_character_id_fkey"),
            ondelete="CASCADE",
        ),
        # RESTRICT: a cited source cannot be deleted.
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("character_appearances_source_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["work_id"],
            ["works.id"],
            name=op.f("character_appearances_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "character_id", "work_id", name=op.f("character_appearances_pkey")
        ),
    )
    op.create_index(
        op.f("ix_character_appearances_source_id"),
        "character_appearances",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_character_appearances_work_id"),
        "character_appearances",
        ["work_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_character_appearances_work_id"), table_name="character_appearances"
    )
    op.drop_index(
        op.f("ix_character_appearances_source_id"), table_name="character_appearances"
    )
    op.drop_table("character_appearances")
