"""Create mobile_suit_relations table.

Revision ID: 51e6444ee7d6
Revises: 641d957f8f39
Create Date: 2026-11-07 22:32:31.167888+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import create_pg_enum, drop_pg_enum

revision: str = "51e6444ee7d6"
down_revision: str | Sequence[str] | None = "641d957f8f39"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MOBILE_SUIT_RELATION_TYPE_VALUES = [
    "variant_of",
    "developed_from",
    "upgrade_of",
    "alternate_version_of",
]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop it (ALEM-11).
    relation_type = create_pg_enum(
        "mobile_suit_relation_type", MOBILE_SUIT_RELATION_TYPE_VALUES
    )
    # A junction table: the edge is the key, with no surrogate ``id``
    # (RDB-2). ``from_mobile_suit_id`` leads the key, so only
    # ``to_mobile_suit_id`` and ``source_id`` need indexes (RDB-18).
    op.create_table(
        "mobile_suit_relations",
        sa.Column("from_mobile_suit_id", sa.Uuid(), nullable=False),
        sa.Column("relation_type", relation_type, nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("to_mobile_suit_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "from_mobile_suit_id <> to_mobile_suit_id",
            name=op.f("ck_mobile_suit_relations_not_self_relation"),
        ),
        # CASCADE on both ends: an edge needs both suits.
        sa.ForeignKeyConstraint(
            ["from_mobile_suit_id"],
            ["mobile_suits.id"],
            name=op.f("mobile_suit_relations_from_mobile_suit_id_fkey"),
            ondelete="CASCADE",
        ),
        # RESTRICT: a source that an edge still cites cannot be deleted.
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("mobile_suit_relations_source_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["to_mobile_suit_id"],
            ["mobile_suits.id"],
            name=op.f("mobile_suit_relations_to_mobile_suit_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "from_mobile_suit_id",
            "relation_type",
            "to_mobile_suit_id",
            name=op.f("mobile_suit_relations_pkey"),
        ),
    )
    op.create_index(
        op.f("ix_mobile_suit_relations_source_id"),
        "mobile_suit_relations",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_mobile_suit_relations_to_mobile_suit_id"),
        "mobile_suit_relations",
        ["to_mobile_suit_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_mobile_suit_relations_to_mobile_suit_id"),
        table_name="mobile_suit_relations",
    )
    op.drop_index(
        op.f("ix_mobile_suit_relations_source_id"), table_name="mobile_suit_relations"
    )
    op.drop_table("mobile_suit_relations")
    drop_pg_enum("mobile_suit_relation_type", MOBILE_SUIT_RELATION_TYPE_VALUES)
