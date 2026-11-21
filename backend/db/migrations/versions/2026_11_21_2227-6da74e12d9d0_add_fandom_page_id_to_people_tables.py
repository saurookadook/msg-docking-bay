"""Add fandom_page_id to characters, designers and organizations.

Revision ID: 6da74e12d9d0
Revises: e65246e18079
Create Date: 2026-11-21 22:27:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "6da74e12d9d0"
down_revision: str | Sequence[str] | None = "e65246e18079"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Nullable: a row can come without a Gundam Wiki page. The loader
    # matches renamed pages on it (D2).
    op.add_column(
        "characters", sa.Column("fandom_page_id", sa.Integer(), nullable=True)
    )
    op.create_unique_constraint(
        op.f("characters_fandom_page_id_key"), "characters", ["fandom_page_id"]
    )
    op.create_check_constraint(
        op.f("ck_characters_fandom_page_id_positive"),
        "characters",
        "fandom_page_id > 0",
    )
    op.add_column(
        "mechanical_designers", sa.Column("fandom_page_id", sa.Integer(), nullable=True)
    )
    op.create_unique_constraint(
        op.f("mechanical_designers_fandom_page_id_key"),
        "mechanical_designers",
        ["fandom_page_id"],
    )
    op.create_check_constraint(
        op.f("ck_mechanical_designers_fandom_page_id_positive"),
        "mechanical_designers",
        "fandom_page_id > 0",
    )
    op.add_column(
        "organizations", sa.Column("fandom_page_id", sa.Integer(), nullable=True)
    )
    op.create_unique_constraint(
        op.f("organizations_fandom_page_id_key"), "organizations", ["fandom_page_id"]
    )
    op.create_check_constraint(
        op.f("ck_organizations_fandom_page_id_positive"),
        "organizations",
        "fandom_page_id > 0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("ck_organizations_fandom_page_id_positive"), "organizations", type_="check"
    )
    op.drop_constraint(
        op.f("organizations_fandom_page_id_key"), "organizations", type_="unique"
    )
    op.drop_column("organizations", "fandom_page_id")
    op.drop_constraint(
        op.f("ck_mechanical_designers_fandom_page_id_positive"),
        "mechanical_designers",
        type_="check",
    )
    op.drop_constraint(
        op.f("mechanical_designers_fandom_page_id_key"),
        "mechanical_designers",
        type_="unique",
    )
    op.drop_column("mechanical_designers", "fandom_page_id")
    op.drop_constraint(
        op.f("ck_characters_fandom_page_id_positive"), "characters", type_="check"
    )
    op.drop_constraint(
        op.f("characters_fandom_page_id_key"), "characters", type_="unique"
    )
    op.drop_column("characters", "fandom_page_id")
