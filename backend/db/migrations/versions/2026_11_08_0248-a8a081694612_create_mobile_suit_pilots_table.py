"""Create mobile_suit_pilots table.

Revision ID: a8a081694612
Revises: f559b761012b
Create Date: 2026-11-08 02:48:48.217369+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a8a081694612"
down_revision: str | Sequence[str] | None = "f559b761012b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # A deliberate deviation from RDB-2 (ALEM-7): ``work_id`` is
    # optional, and a primary key column cannot be null, so the link has
    # a surrogate ``id`` and a UNIQUE NULLS NOT DISTINCT key instead
    # (PostgreSQL 15+), allowing one "work unknown" row per pair.
    op.create_table(
        "mobile_suit_pilots",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("character_id", sa.Uuid(), nullable=False),
        sa.Column("mobile_suit_id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        # Nullable: a page may not say which work they pilot it in.
        sa.Column("work_id", sa.Uuid(), nullable=True),
        # Composite FKs to the appearances: "piloted in W" implies the
        # character and the suit both appear in W. MATCH SIMPLE skips
        # them when ``work_id`` is null, so plain FKs check the
        # character and the suit too. CASCADE throughout.
        sa.ForeignKeyConstraint(
            ["character_id", "work_id"],
            ["character_appearances.character_id", "character_appearances.work_id"],
            name=op.f("mobile_suit_pilots_character_id_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
            name=op.f("mobile_suit_pilots_character_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["mobile_suit_id", "work_id"],
            [
                "mobile_suit_appearances.mobile_suit_id",
                "mobile_suit_appearances.work_id",
            ],
            name=op.f("mobile_suit_pilots_mobile_suit_id_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["mobile_suit_id"],
            ["mobile_suits.id"],
            name=op.f("mobile_suit_pilots_mobile_suit_id_fkey"),
            ondelete="CASCADE",
        ),
        # RESTRICT: a cited source cannot be deleted.
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("mobile_suit_pilots_source_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("mobile_suit_pilots_pkey")),
        sa.UniqueConstraint(
            "character_id",
            "mobile_suit_id",
            "work_id",
            name=op.f("mobile_suit_pilots_character_id_mobile_suit_id_work_id_key"),
            postgresql_nulls_not_distinct=True,
        ),
    )
    # The composite FKs' indexes also cover the plain FKs they lead.
    op.create_index(
        "ix_mobile_suit_pilots_character_id_work_id",
        "mobile_suit_pilots",
        ["character_id", "work_id"],
        unique=False,
    )
    op.create_index(
        "ix_mobile_suit_pilots_mobile_suit_id_work_id",
        "mobile_suit_pilots",
        ["mobile_suit_id", "work_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_mobile_suit_pilots_source_id"),
        "mobile_suit_pilots",
        ["source_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_mobile_suit_pilots_source_id"), table_name="mobile_suit_pilots"
    )
    op.drop_index(
        "ix_mobile_suit_pilots_mobile_suit_id_work_id", table_name="mobile_suit_pilots"
    )
    op.drop_index(
        "ix_mobile_suit_pilots_character_id_work_id", table_name="mobile_suit_pilots"
    )
    op.drop_table("mobile_suit_pilots")
