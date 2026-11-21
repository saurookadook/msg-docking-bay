"""Create work_slug_redirects table.

Revision ID: 7818b2534cce
Revises: c3bb65c7583c
Create Date: 2026-11-21 21:04:03.554344+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "7818b2534cce"
down_revision: str | Sequence[str] | None = "c3bb65c7583c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keyed on the old slug, with no surrogate ``id`` (D2). The work's
    # foreign key does not lead the key, so it is indexed (RDB-18).
    op.create_table(
        "work_slug_redirects",
        sa.Column("old_slug", sa.TEXT(), nullable=False),
        sa.Column("work_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "old_slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_work_slug_redirects_old_slug_format"),
        ),
        # CASCADE: a deleted work takes its old slugs with it.
        sa.ForeignKeyConstraint(
            ["work_id"],
            ["works.id"],
            name=op.f("work_slug_redirects_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("old_slug", name=op.f("work_slug_redirects_pkey")),
    )
    op.create_index(
        op.f("ix_work_slug_redirects_work_id"),
        "work_slug_redirects",
        ["work_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_work_slug_redirects_work_id"), table_name="work_slug_redirects"
    )
    op.drop_table("work_slug_redirects")
