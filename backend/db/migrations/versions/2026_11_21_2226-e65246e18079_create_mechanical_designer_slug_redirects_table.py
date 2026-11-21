"""Create mechanical_designer_slug_redirects table.

Revision ID: e65246e18079
Revises: 8bf96e94b85d
Create Date: 2026-11-21 22:26:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e65246e18079"
down_revision: str | Sequence[str] | None = "8bf96e94b85d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keyed on the old slug, with no surrogate ``id`` (D2). The
    # mechanical designer's foreign key does not lead the key, so it
    # is indexed (RDB-18).
    op.create_table(
        "mechanical_designer_slug_redirects",
        sa.Column("old_slug", sa.TEXT(), nullable=False),
        sa.Column("mechanical_designer_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "old_slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_mechanical_designer_slug_redirects_old_slug_format"),
        ),
        # CASCADE: a deleted designer takes their old slugs with it.
        sa.ForeignKeyConstraint(
            ["mechanical_designer_id"],
            ["mechanical_designers.id"],
            name=op.f("mechanical_designer_slug_redirects_mechanical_designer_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "old_slug", name=op.f("mechanical_designer_slug_redirects_pkey")
        ),
    )
    op.create_index(
        op.f("ix_mechanical_designer_slug_redirects_mechanical_designer_id"),
        "mechanical_designer_slug_redirects",
        ["mechanical_designer_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_mechanical_designer_slug_redirects_mechanical_designer_id"),
        table_name="mechanical_designer_slug_redirects",
    )
    op.drop_table("mechanical_designer_slug_redirects")
