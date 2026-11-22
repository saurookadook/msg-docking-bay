"""Create character_slug_redirects table.

Revision ID: dd12e8b0c46e
Revises: 2e48e9ec3b2d
Create Date: 2026-11-21 22:24:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "dd12e8b0c46e"
down_revision: str | Sequence[str] | None = "2e48e9ec3b2d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keyed on the old slug, with no surrogate ``id`` (D2, RDB-13). The
    # character's foreign key does not lead the key, so it
    # is indexed (RDB-18).
    op.create_table(
        "character_slug_redirects",
        sa.Column("character_id", sa.Uuid(), nullable=False),
        sa.Column("old_slug", sa.TEXT(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "old_slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_character_slug_redirects_old_slug_format"),
        ),
        # CASCADE: a deleted character takes their old slugs with it.
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
            name=op.f("character_slug_redirects_character_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("old_slug", name=op.f("character_slug_redirects_pkey")),
    )
    op.create_index(
        op.f("ix_character_slug_redirects_character_id"),
        "character_slug_redirects",
        ["character_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_character_slug_redirects_character_id"),
        table_name="character_slug_redirects",
    )
    op.drop_table("character_slug_redirects")
