"""Create mobile_suit_slug_redirects table.

Revision ID: c3bb65c7583c
Revises: 16a6adcc4df8
Create Date: 2026-11-21 21:03:39.571863+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c3bb65c7583c"
down_revision: str | Sequence[str] | None = "16a6adcc4df8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keyed on the old slug, with no surrogate ``id`` (D2). The suit's
    # foreign key does not lead the key, so it is indexed (RDB-18).
    op.create_table(
        "mobile_suit_slug_redirects",
        sa.Column("mobile_suit_id", sa.Uuid(), nullable=False),
        sa.Column("old_slug", sa.TEXT(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "old_slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_mobile_suit_slug_redirects_old_slug_format"),
        ),
        # CASCADE: a deleted suit takes its old slugs with it.
        sa.ForeignKeyConstraint(
            ["mobile_suit_id"],
            ["mobile_suits.id"],
            name=op.f("mobile_suit_slug_redirects_mobile_suit_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "old_slug", name=op.f("mobile_suit_slug_redirects_pkey")
        ),
    )
    op.create_index(
        op.f("ix_mobile_suit_slug_redirects_mobile_suit_id"),
        "mobile_suit_slug_redirects",
        ["mobile_suit_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_mobile_suit_slug_redirects_mobile_suit_id"),
        table_name="mobile_suit_slug_redirects",
    )
    op.drop_table("mobile_suit_slug_redirects")
