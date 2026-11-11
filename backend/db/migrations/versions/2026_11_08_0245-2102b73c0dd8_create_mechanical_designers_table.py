"""Create mechanical_designers table.

Revision ID: 2102b73c0dd8
Revises: 996f52343021
Create Date: 2026-11-08 02:44:53.388465+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2102b73c0dd8"
down_revision: str | Sequence[str] | None = "996f52343021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Real people, kept apart from the fictional ``characters``.
    op.create_table(
        "mechanical_designers",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fandom_page_title", sa.TEXT(), nullable=True),
        # Not unique: people are told apart by slug.
        sa.Column("name", sa.TEXT(), nullable=False),
        sa.Column("name_ja", sa.TEXT(), nullable=True),
        sa.Column("slug", sa.TEXT(), nullable=False),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_mechanical_designers_slug_format"),
        ),
        sa.CheckConstraint(
            "char_length(fandom_page_title) > 0",
            name=op.f("ck_mechanical_designers_fandom_page_title_not_empty"),
        ),
        sa.CheckConstraint(
            "char_length(name) > 0", name=op.f("ck_mechanical_designers_name_not_empty")
        ),
        sa.CheckConstraint(
            "char_length(name_ja) > 0",
            name=op.f("ck_mechanical_designers_name_ja_not_empty"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("mechanical_designers_pkey")),
        sa.UniqueConstraint(
            "fandom_page_title", name=op.f("mechanical_designers_fandom_page_title_key")
        ),
        sa.UniqueConstraint("slug", name=op.f("mechanical_designers_slug_key")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("mechanical_designers")
