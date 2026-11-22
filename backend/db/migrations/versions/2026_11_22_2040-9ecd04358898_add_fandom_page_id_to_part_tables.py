"""Add fandom_page_id to part tables.

The part tables are ``armaments``, ``equipment``, ``materials`` and
``powerplants``.

Revision ID: 9ecd04358898
Revises: 6da74e12d9d0
Create Date: 2026-11-22 20:40:20.869324+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9ecd04358898"
down_revision: str | Sequence[str] | None = "6da74e12d9d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Nullable: most parts have no Gundam Wiki page of their own. The
    # loader matches renamed pages on it (D2, amended for PR D).
    op.add_column("armaments", sa.Column("fandom_page_id", sa.Integer(), nullable=True))
    op.create_unique_constraint(
        op.f("armaments_fandom_page_id_key"), "armaments", ["fandom_page_id"]
    )
    # NOTE: autogenerate does not see check constraints, so each
    # ``positive`` check is added by hand (ALEM-6).
    op.create_check_constraint(
        op.f("ck_armaments_fandom_page_id_positive"), "armaments", "fandom_page_id > 0"
    )
    op.add_column("equipment", sa.Column("fandom_page_id", sa.Integer(), nullable=True))
    op.create_unique_constraint(
        op.f("equipment_fandom_page_id_key"), "equipment", ["fandom_page_id"]
    )
    op.create_check_constraint(
        op.f("ck_equipment_fandom_page_id_positive"), "equipment", "fandom_page_id > 0"
    )
    op.add_column("materials", sa.Column("fandom_page_id", sa.Integer(), nullable=True))
    op.create_unique_constraint(
        op.f("materials_fandom_page_id_key"), "materials", ["fandom_page_id"]
    )
    op.create_check_constraint(
        op.f("ck_materials_fandom_page_id_positive"), "materials", "fandom_page_id > 0"
    )
    op.add_column(
        "powerplants", sa.Column("fandom_page_id", sa.Integer(), nullable=True)
    )
    op.create_unique_constraint(
        op.f("powerplants_fandom_page_id_key"), "powerplants", ["fandom_page_id"]
    )
    op.create_check_constraint(
        op.f("ck_powerplants_fandom_page_id_positive"),
        "powerplants",
        "fandom_page_id > 0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("ck_powerplants_fandom_page_id_positive"), "powerplants", type_="check"
    )
    op.drop_constraint(
        op.f("powerplants_fandom_page_id_key"), "powerplants", type_="unique"
    )
    op.drop_column("powerplants", "fandom_page_id")
    op.drop_constraint(
        op.f("ck_materials_fandom_page_id_positive"), "materials", type_="check"
    )
    op.drop_constraint(
        op.f("materials_fandom_page_id_key"), "materials", type_="unique"
    )
    op.drop_column("materials", "fandom_page_id")
    op.drop_constraint(
        op.f("ck_equipment_fandom_page_id_positive"), "equipment", type_="check"
    )
    op.drop_constraint(
        op.f("equipment_fandom_page_id_key"), "equipment", type_="unique"
    )
    op.drop_column("equipment", "fandom_page_id")
    op.drop_constraint(
        op.f("ck_armaments_fandom_page_id_positive"), "armaments", type_="check"
    )
    op.drop_constraint(
        op.f("armaments_fandom_page_id_key"), "armaments", type_="unique"
    )
    op.drop_column("armaments", "fandom_page_id")
