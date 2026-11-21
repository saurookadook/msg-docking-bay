"""Create organization_slug_redirects table.

Revision ID: 8bf96e94b85d
Revises: dd12e8b0c46e
Create Date: 2026-11-21 22:25:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "8bf96e94b85d"
down_revision: str | Sequence[str] | None = "dd12e8b0c46e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keyed on the old slug, with no surrogate ``id`` (D2). The
    # organization's foreign key does not lead the key, so it
    # is indexed (RDB-18).
    op.create_table(
        "organization_slug_redirects",
        sa.Column("old_slug", sa.TEXT(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "old_slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_organization_slug_redirects_old_slug_format"),
        ),
        # CASCADE: a deleted organization takes its old slugs with it.
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("organization_slug_redirects_organization_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "old_slug", name=op.f("organization_slug_redirects_pkey")
        ),
    )
    op.create_index(
        op.f("ix_organization_slug_redirects_organization_id"),
        "organization_slug_redirects",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_organization_slug_redirects_organization_id"),
        table_name="organization_slug_redirects",
    )
    op.drop_table("organization_slug_redirects")
