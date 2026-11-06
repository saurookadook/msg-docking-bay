"""Create work_short_names table.

Revision ID: 61c9560b6d31
Revises: 8a5f12aac571
Create Date: 2026-11-01 19:11:34.391908+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "61c9560b6d31"
down_revision: str | Sequence[str] | None = "8a5f12aac571"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "work_short_names",
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
        sa.Column("short_name", sa.TEXT(), nullable=False),
        sa.Column("work_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint(
            "char_length(short_name) > 0",
            name=op.f("ck_work_short_names_short_name_not_empty"),
        ),
        # Tags are parsed out of "Amuro Ray [MSG]"; stray spaces would
        # make " MSG" and "MSG" two tags for one work.
        sa.CheckConstraint(
            "short_name = btrim(short_name)",
            name=op.f("ck_work_short_names_short_name_trimmed"),
        ),
        # CASCADE: a tag means nothing without its work (RDB-15).
        sa.ForeignKeyConstraint(
            ["work_id"],
            ["works.id"],
            name=op.f("work_short_names_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("work_short_names_pkey")),
        # Unique, so each tag resolves to exactly one work (RDB-13).
        sa.UniqueConstraint("short_name", name=op.f("work_short_names_short_name_key")),
    )
    op.create_index(
        op.f("ix_work_short_names_work_id"),
        "work_short_names",
        ["work_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_work_short_names_work_id"), table_name="work_short_names")
    op.drop_table("work_short_names")
