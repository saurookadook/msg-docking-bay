"""Create works table.

Revision ID: 8a5f12aac571
Revises: dc737af782aa
Create Date: 2026-11-01 19:06:04.089517+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import create_pg_enum, drop_pg_enum

revision: str = "8a5f12aac571"
down_revision: str | Sequence[str] | None = "dc737af782aa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORK_TYPE_VALUES = [
    "tv_series",
    "film",
    "ova",
    "ona",
    "manga",
    "novel",
    "video_game",
    "other",
]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop it (ALEM-11).
    work_type = create_pg_enum("work_type", WORK_TYPE_VALUES)
    op.create_table(
        "works",
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
        # External IDs are nullable: most works lack at least one, and
        # each is unique when present (RDB-13).
        sa.Column("anilist_id", sa.Integer(), nullable=True),
        sa.Column("ann_id", sa.Integer(), nullable=True),
        # Nullable: crossovers such as G Generation span timelines.
        sa.Column("continuity_id", sa.Uuid(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("fandom_page_title", sa.TEXT(), nullable=True),
        # Nullable: only seasons and parts point at a parent series.
        sa.Column("parent_work_id", sa.Uuid(), nullable=True),
        sa.Column("slug", sa.TEXT(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        # Not unique: a TV series and a video game can share a title.
        sa.Column("title", sa.TEXT(), nullable=False),
        sa.Column("title_ja", sa.TEXT(), nullable=True),
        sa.Column("wikidata_qid", sa.TEXT(), nullable=True),
        sa.Column("work_type", work_type, nullable=False),
        sa.CheckConstraint("anilist_id > 0", name=op.f("ck_works_anilist_id_positive")),
        sa.CheckConstraint("ann_id > 0", name=op.f("ck_works_ann_id_positive")),
        # A NULL on either side passes, so open-ended works are allowed.
        sa.CheckConstraint(
            "end_date >= start_date", name=op.f("ck_works_end_after_start")
        ),
        sa.CheckConstraint(
            "char_length(fandom_page_title) > 0",
            name=op.f("ck_works_fandom_page_title_not_empty"),
        ),
        sa.CheckConstraint(
            "parent_work_id <> id", name=op.f("ck_works_not_own_parent")
        ),
        sa.CheckConstraint(
            "slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'", name=op.f("ck_works_slug_format")
        ),
        sa.CheckConstraint(
            "char_length(title) > 0", name=op.f("ck_works_title_not_empty")
        ),
        sa.CheckConstraint(
            "char_length(title_ja) > 0", name=op.f("ck_works_title_ja_not_empty")
        ),
        sa.CheckConstraint(
            "wikidata_qid ~ '^Q[0-9]+$'", name=op.f("ck_works_wikidata_qid_format")
        ),
        # SET NULL on both: deleting a timeline or a series leaves its
        # works in place, unlinked, rather than deleting them (RDB-15).
        sa.ForeignKeyConstraint(
            ["continuity_id"],
            ["continuities.id"],
            name=op.f("works_continuity_id_fkey"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["parent_work_id"],
            ["works.id"],
            name=op.f("works_parent_work_id_fkey"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("works_pkey")),
        sa.UniqueConstraint("anilist_id", name=op.f("works_anilist_id_key")),
        sa.UniqueConstraint("ann_id", name=op.f("works_ann_id_key")),
        sa.UniqueConstraint(
            "fandom_page_title", name=op.f("works_fandom_page_title_key")
        ),
        sa.UniqueConstraint("slug", name=op.f("works_slug_key")),
        sa.UniqueConstraint("wikidata_qid", name=op.f("works_wikidata_qid_key")),
    )
    op.create_index(
        op.f("ix_works_continuity_id"), "works", ["continuity_id"], unique=False
    )
    op.create_index(
        op.f("ix_works_parent_work_id"), "works", ["parent_work_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_works_parent_work_id"), table_name="works")
    op.drop_index(op.f("ix_works_continuity_id"), table_name="works")
    op.drop_table("works")
    drop_pg_enum("work_type", WORK_TYPE_VALUES)
