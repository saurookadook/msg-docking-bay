"""Create mobile_suit_designers table.

Revision ID: 16a6adcc4df8
Revises: a24dd59162d4
Create Date: 2026-11-08 02:54:02.486747+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "16a6adcc4df8"
down_revision: str | Sequence[str] | None = "a24dd59162d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # A junction table keyed on (designer, suit), with no surrogate
    # ``id`` (RDB-2). ``mechanical_designer_id`` leads the key, so only
    # ``mobile_suit_id`` and ``source_id`` need indexes (RDB-18).
    op.create_table(
        "mobile_suit_designers",
        sa.Column("mechanical_designer_id", sa.Uuid(), nullable=False),
        sa.Column("mobile_suit_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # RESTRICT: a designer a suit still credits cannot be deleted.
        sa.ForeignKeyConstraint(
            ["mechanical_designer_id"],
            ["mechanical_designers.id"],
            name=op.f("mobile_suit_designers_mechanical_designer_id_fkey"),
            ondelete="RESTRICT",
        ),
        # CASCADE: deleting the suit removes its credits.
        sa.ForeignKeyConstraint(
            ["mobile_suit_id"],
            ["mobile_suits.id"],
            name=op.f("mobile_suit_designers_mobile_suit_id_fkey"),
            ondelete="CASCADE",
        ),
        # RESTRICT: a cited source cannot be deleted.
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("mobile_suit_designers_source_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "mechanical_designer_id",
            "mobile_suit_id",
            name=op.f("mobile_suit_designers_pkey"),
        ),
    )
    op.create_index(
        op.f("ix_mobile_suit_designers_mobile_suit_id"),
        "mobile_suit_designers",
        ["mobile_suit_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_mobile_suit_designers_source_id"),
        "mobile_suit_designers",
        ["source_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_mobile_suit_designers_source_id"), table_name="mobile_suit_designers"
    )
    op.drop_index(
        op.f("ix_mobile_suit_designers_mobile_suit_id"),
        table_name="mobile_suit_designers",
    )
    op.drop_table("mobile_suit_designers")
