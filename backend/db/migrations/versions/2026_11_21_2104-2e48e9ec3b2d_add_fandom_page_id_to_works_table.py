"""Add fandom_page_id to works table.

Revision ID: 2e48e9ec3b2d
Revises: 7818b2534cce
Create Date: 2026-11-21 21:04:27.016265+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "2e48e9ec3b2d"
down_revision: str | Sequence[str] | None = "7818b2534cce"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Nullable: a work can come from Wikidata alone, with no Gundam Wiki
    # page. The loader matches renamed pages on it (D2).
    op.add_column("works", sa.Column("fandom_page_id", sa.Integer(), nullable=True))
    op.create_unique_constraint(
        op.f("works_fandom_page_id_key"), "works", ["fandom_page_id"]
    )
    op.create_check_constraint(
        op.f("ck_works_fandom_page_id_positive"), "works", "fandom_page_id > 0"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("ck_works_fandom_page_id_positive"), "works", type_="check")
    op.drop_constraint(op.f("works_fandom_page_id_key"), "works", type_="unique")
    op.drop_column("works", "fandom_page_id")
