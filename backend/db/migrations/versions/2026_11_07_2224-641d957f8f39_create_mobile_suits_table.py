"""Create mobile_suits table.

Revision ID: 641d957f8f39
Revises: 71aaa31e79ec
Create Date: 2026-11-07 22:24:22.594169+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import create_pg_enum, drop_pg_enum

revision: str = "641d957f8f39"
down_revision: str | Sequence[str] | None = "71aaa31e79ec"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UNIT_TYPE_VALUES = [
    "suit",
    "armor",
    "fighter",
    "man_machine",
    "worker",
    "pod",
    "doll",
]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop it (ALEM-11).
    unit_type = create_pg_enum("unit_type", UNIT_TYPE_VALUES)
    op.create_table(
        "mobile_suits",
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
        # Nullable: a page with no infobox ``era`` has no timeline.
        sa.Column("continuity_id", sa.Uuid(), nullable=True),
        # The page ID survives a rename; unique when present (RDB-13).
        sa.Column("fandom_page_id", sa.Integer(), nullable=True),
        # Not unique: versions of one unit can share a model number.
        sa.Column("model_number", sa.TEXT(), nullable=True),
        # Not unique: pages are told apart by slug and page ID.
        sa.Column("name", sa.TEXT(), nullable=False),
        sa.Column("name_ja", sa.TEXT(), nullable=True),
        sa.Column("slug", sa.TEXT(), nullable=False),
        sa.Column("unit_type", unit_type, nullable=False),
        sa.CheckConstraint(
            "fandom_page_id > 0", name=op.f("ck_mobile_suits_fandom_page_id_positive")
        ),
        sa.CheckConstraint(
            "char_length(model_number) > 0",
            name=op.f("ck_mobile_suits_model_number_not_empty"),
        ),
        sa.CheckConstraint(
            "char_length(name) > 0", name=op.f("ck_mobile_suits_name_not_empty")
        ),
        sa.CheckConstraint(
            "char_length(name_ja) > 0", name=op.f("ck_mobile_suits_name_ja_not_empty")
        ),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'",
            name=op.f("ck_mobile_suits_slug_format"),
        ),
        # SET NULL: deleting a timeline leaves its suits in place,
        # unlinked, rather than deleting them (RDB-15).
        sa.ForeignKeyConstraint(
            ["continuity_id"],
            ["continuities.id"],
            name=op.f("mobile_suits_continuity_id_fkey"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("mobile_suits_pkey")),
        sa.UniqueConstraint(
            "fandom_page_id", name=op.f("mobile_suits_fandom_page_id_key")
        ),
        sa.UniqueConstraint("slug", name=op.f("mobile_suits_slug_key")),
    )
    op.create_index(
        op.f("ix_mobile_suits_continuity_id"),
        "mobile_suits",
        ["continuity_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_mobile_suits_continuity_id"), table_name="mobile_suits")
    op.drop_table("mobile_suits")
    drop_pg_enum("unit_type", UNIT_TYPE_VALUES)
