"""Create organization_appearances table.

Revision ID: f559b761012b
Revises: 21f9f46a85ea
Create Date: 2026-11-08 02:47:26.521810+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f559b761012b"
down_revision: str | Sequence[str] | None = "21f9f46a85ea"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # A junction table keyed on (organization, work), with no
    # surrogate ``id`` (RDB-2). ``organization_id`` leads the key, so
    # only ``work_id`` and ``source_id`` need indexes (RDB-18).
    op.create_table(
        "organization_appearances",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("work_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # CASCADE on organization and work: an appearance needs both.
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("organization_appearances_organization_id_fkey"),
            ondelete="CASCADE",
        ),
        # RESTRICT: a cited source cannot be deleted.
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("organization_appearances_source_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["work_id"],
            ["works.id"],
            name=op.f("organization_appearances_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "organization_id", "work_id", name=op.f("organization_appearances_pkey")
        ),
    )
    op.create_index(
        op.f("ix_organization_appearances_source_id"),
        "organization_appearances",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_appearances_work_id"),
        "organization_appearances",
        ["work_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_organization_appearances_work_id"),
        table_name="organization_appearances",
    )
    op.drop_index(
        op.f("ix_organization_appearances_source_id"),
        table_name="organization_appearances",
    )
    op.drop_table("organization_appearances")
