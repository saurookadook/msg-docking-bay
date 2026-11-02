"""Create continuities table.

Revision ID: dc737af782aa
Revises:
Create Date: 2026-11-01 18:12:31.182916+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "dc737af782aa"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "continuities",
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
        sa.Column("name", sa.TEXT(), nullable=False),
        # Nullable: most timelines are roots. A branch, such as GQ's
        # alternate Universal Century, points at the one it splits from.
        sa.Column("parent_continuity_id", sa.Uuid(), nullable=True),
        sa.Column("slug", sa.TEXT(), nullable=False),
        sa.CheckConstraint(
            "char_length(name) > 0", name=op.f("ck_continuities_name_not_empty")
        ),
        sa.CheckConstraint(
            "parent_continuity_id <> id", name=op.f("ck_continuities_not_own_parent")
        ),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_continuities_slug_format"),
        ),
        # SET NULL: deleting a timeline turns its branches into roots
        # rather than deleting them (RDB-15).
        sa.ForeignKeyConstraint(
            ["parent_continuity_id"],
            ["continuities.id"],
            name=op.f("continuities_parent_continuity_id_fkey"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("continuities_pkey")),
        sa.UniqueConstraint("name", name=op.f("continuities_name_key")),
        sa.UniqueConstraint("slug", name=op.f("continuities_slug_key")),
    )
    op.create_index(
        op.f("ix_continuities_parent_continuity_id"),
        "continuities",
        ["parent_continuity_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_continuities_parent_continuity_id"), table_name="continuities"
    )
    op.drop_table("continuities")
