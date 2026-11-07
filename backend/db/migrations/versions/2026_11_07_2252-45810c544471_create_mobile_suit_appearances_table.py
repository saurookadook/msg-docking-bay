"""Create mobile_suit_appearances table.

Revision ID: 45810c544471
Revises: 51e6444ee7d6
Create Date: 2026-11-07 22:52:14.633513+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "45810c544471"
down_revision: str | Sequence[str] | None = "51e6444ee7d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # A junction table keyed on (suit, work), with no surrogate ``id``
    # (RDB-2). ``mobile_suit_id`` leads the key, so only ``work_id`` and
    # ``source_id`` need indexes (RDB-18).
    op.create_table(
        "mobile_suit_appearances",
        # Nullable: a film has no episodes; ranges are often unknown.
        sa.Column("first_episode", sa.Integer(), nullable=True),
        sa.Column(
            "is_debut", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("last_episode", sa.Integer(), nullable=True),
        sa.Column("mobile_suit_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("work_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "first_episode > 0",
            name=op.f("ck_mobile_suit_appearances_first_episode_positive"),
        ),
        sa.CheckConstraint(
            "last_episode >= first_episode",
            name=op.f("ck_mobile_suit_appearances_episodes_in_order"),
        ),
        # A range needs its start: a last episode alone means nothing.
        sa.CheckConstraint(
            "last_episode IS NULL OR first_episode IS NOT NULL",
            name=op.f("ck_mobile_suit_appearances_last_episode_needs_first"),
        ),
        # CASCADE on suit and work: an appearance needs both.
        sa.ForeignKeyConstraint(
            ["mobile_suit_id"],
            ["mobile_suits.id"],
            name=op.f("mobile_suit_appearances_mobile_suit_id_fkey"),
            ondelete="CASCADE",
        ),
        # RESTRICT: a cited source cannot be deleted.
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("mobile_suit_appearances_source_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["work_id"],
            ["works.id"],
            name=op.f("mobile_suit_appearances_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "mobile_suit_id", "work_id", name=op.f("mobile_suit_appearances_pkey")
        ),
    )
    op.create_index(
        op.f("ix_mobile_suit_appearances_source_id"),
        "mobile_suit_appearances",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_mobile_suit_appearances_work_id"),
        "mobile_suit_appearances",
        ["work_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_mobile_suit_appearances_work_id"), table_name="mobile_suit_appearances"
    )
    op.drop_index(
        op.f("ix_mobile_suit_appearances_source_id"),
        table_name="mobile_suit_appearances",
    )
    op.drop_table("mobile_suit_appearances")
