"""Create powerplants table.

Revision ID: 351ca28410b5
Revises: 9d0ed1fbb821
Create Date: 2026-11-07 23:06:10.121825+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "351ca28410b5"
down_revision: str | Sequence[str] | None = "9d0ed1fbb821"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # One row per part, however many sheets list it (ADR 0002).
    op.create_table(
        "powerplants",
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
        sa.Column("name", sa.TEXT(), nullable=False),
        sa.Column("slug", sa.TEXT(), nullable=False),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name=op.f("ck_powerplants_slug_format")
        ),
        sa.CheckConstraint(
            "char_length(fandom_page_title) > 0",
            name=op.f("ck_powerplants_fandom_page_title_not_empty"),
        ),
        sa.CheckConstraint(
            "char_length(name) > 0", name=op.f("ck_powerplants_name_not_empty")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("powerplants_pkey")),
        sa.UniqueConstraint(
            "fandom_page_title", name=op.f("powerplants_fandom_page_title_key")
        ),
        sa.UniqueConstraint("slug", name=op.f("powerplants_slug_key")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("powerplants")
