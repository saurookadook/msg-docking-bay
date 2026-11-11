"""Create mobile_suit_organizations table.

Revision ID: a24dd59162d4
Revises: a8a081694612
Create Date: 2026-11-08 02:50:53.093600+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import create_pg_enum, drop_pg_enum

revision: str = "a24dd59162d4"
down_revision: str | Sequence[str] | None = "a8a081694612"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MOBILE_SUIT_ORGANIZATION_ROLE_VALUES = ["manufacturer", "operator", "developer"]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop it (ALEM-11).
    role = create_pg_enum(
        "mobile_suit_organization_role", MOBILE_SUIT_ORGANIZATION_ROLE_VALUES
    )
    # The same deliberate deviation from RDB-2 as mobile_suit_pilots
    # (ALEM-7): ``work_id`` is optional, so the link has a surrogate
    # ``id`` and a UNIQUE NULLS NOT DISTINCT key, with the role in it.
    op.create_table(
        "mobile_suit_organizations",
        sa.Column("id", sa.Uuid(), server_default=sa.text("uuidv7()"), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("mobile_suit_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("role", role, nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        # Nullable: a page may not say which work the role is in.
        sa.Column("work_id", sa.Uuid(), nullable=True),
        # Composite FKs to the appearances: "operated in W" implies the
        # organization and the suit both appear in W. MATCH SIMPLE
        # skips them when ``work_id`` is null, so plain FKs check the
        # organization and the suit too. CASCADE throughout.
        sa.ForeignKeyConstraint(
            ["mobile_suit_id", "work_id"],
            [
                "mobile_suit_appearances.mobile_suit_id",
                "mobile_suit_appearances.work_id",
            ],
            name=op.f("mobile_suit_organizations_mobile_suit_id_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["mobile_suit_id"],
            ["mobile_suits.id"],
            name=op.f("mobile_suit_organizations_mobile_suit_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id", "work_id"],
            [
                "organization_appearances.organization_id",
                "organization_appearances.work_id",
            ],
            name=op.f("mobile_suit_organizations_organization_id_work_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("mobile_suit_organizations_organization_id_fkey"),
            ondelete="CASCADE",
        ),
        # RESTRICT: a cited source cannot be deleted.
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("mobile_suit_organizations_source_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("mobile_suit_organizations_pkey")),
        sa.UniqueConstraint(
            "mobile_suit_id",
            "organization_id",
            "role",
            "work_id",
            # Named by hand: the derived name is over 63 characters.
            name="mobile_suit_organizations_link_key",
            postgresql_nulls_not_distinct=True,
        ),
    )
    # The composite FKs' indexes also cover the plain FKs they lead.
    op.create_index(
        "ix_mobile_suit_organizations_mobile_suit_id_work_id",
        "mobile_suit_organizations",
        ["mobile_suit_id", "work_id"],
        unique=False,
    )
    op.create_index(
        "ix_mobile_suit_organizations_organization_id_work_id",
        "mobile_suit_organizations",
        ["organization_id", "work_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_mobile_suit_organizations_source_id"),
        "mobile_suit_organizations",
        ["source_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_mobile_suit_organizations_source_id"),
        table_name="mobile_suit_organizations",
    )
    op.drop_index(
        "ix_mobile_suit_organizations_organization_id_work_id",
        table_name="mobile_suit_organizations",
    )
    op.drop_index(
        "ix_mobile_suit_organizations_mobile_suit_id_work_id",
        table_name="mobile_suit_organizations",
    )
    op.drop_table("mobile_suit_organizations")
    drop_pg_enum("mobile_suit_organization_role", MOBILE_SUIT_ORGANIZATION_ROLE_VALUES)
