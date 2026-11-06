"""Create work_relations table.

Revision ID: cf9f30ef9574
Revises: 61c9560b6d31
Create Date: 2026-11-01 20:05:32.482241+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import create_pg_enum, drop_pg_enum

revision: str = "cf9f30ef9574"
down_revision: str | Sequence[str] | None = "61c9560b6d31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORK_RELATION_TYPE_VALUES = [
    "sequel_of",
    "compilation_of",
    "adaptation_of",
    "remake_of",
    "side_story_of",
]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop it (ALEM-11).
    work_relation_type = create_pg_enum("work_relation_type", WORK_RELATION_TYPE_VALUES)
    # A junction table: the edge is the key, with no surrogate ``id``
    # (RDB-2). ``from_work_id`` leads the key, so only ``to_work_id``
    # needs its own index (RDB-18).
    op.create_table(
        "work_relations",
        sa.Column("from_work_id", sa.Uuid(), nullable=False),
        sa.Column("relation_type", work_relation_type, nullable=False),
        sa.Column("to_work_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "from_work_id <> to_work_id",
            name=op.f("ck_work_relations_not_self_relation"),
        ),
        sa.ForeignKeyConstraint(
            ["from_work_id"],
            ["works.id"],
            name=op.f("work_relations_from_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["to_work_id"],
            ["works.id"],
            name=op.f("work_relations_to_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "from_work_id",
            "relation_type",
            "to_work_id",
            name=op.f("work_relations_pkey"),
        ),
    )
    op.create_index(
        op.f("ix_work_relations_to_work_id"),
        "work_relations",
        ["to_work_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_work_relations_to_work_id"), table_name="work_relations")
    op.drop_table("work_relations")
    drop_pg_enum("work_relation_type", WORK_RELATION_TYPE_VALUES)
