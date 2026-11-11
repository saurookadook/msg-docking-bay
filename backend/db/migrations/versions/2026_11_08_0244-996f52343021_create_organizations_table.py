"""Create organizations table.

Revision ID: 996f52343021
Revises: f7df23ff83f2
Create Date: 2026-11-08 02:44:00.466786+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "996f52343021"
down_revision: str | Sequence[str] | None = "f7df23ff83f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # One row per organization; sub-units nest through a parent link
    # (RDB-7).
    op.create_table(
        "organizations",
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
        # Not unique: organizations are told apart by slug.
        sa.Column("name", sa.TEXT(), nullable=False),
        # Nullable: a top-level organization has no parent.
        sa.Column("parent_organization_id", sa.Uuid(), nullable=True),
        sa.Column("slug", sa.TEXT(), nullable=False),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_organizations_slug_format"),
        ),
        sa.CheckConstraint(
            "char_length(fandom_page_title) > 0",
            name=op.f("ck_organizations_fandom_page_title_not_empty"),
        ),
        sa.CheckConstraint(
            "char_length(name) > 0", name=op.f("ck_organizations_name_not_empty")
        ),
        sa.CheckConstraint(
            "parent_organization_id <> id", name=op.f("ck_organizations_not_own_parent")
        ),
        # SET NULL: deleting an organization leaves its units in place,
        # top-level, rather than deleting them (RDB-15).
        sa.ForeignKeyConstraint(
            ["parent_organization_id"],
            ["organizations.id"],
            name=op.f("organizations_parent_organization_id_fkey"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("organizations_pkey")),
        sa.UniqueConstraint(
            "fandom_page_title", name=op.f("organizations_fandom_page_title_key")
        ),
        sa.UniqueConstraint("slug", name=op.f("organizations_slug_key")),
    )
    op.create_index(
        op.f("ix_organizations_parent_organization_id"),
        "organizations",
        ["parent_organization_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_organizations_parent_organization_id"), table_name="organizations"
    )
    op.drop_table("organizations")
