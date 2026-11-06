"""Create sources table.

Revision ID: f284c22290a9
Revises: cf9f30ef9574
Create Date: 2026-11-01 20:21:19.113234+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import create_pg_enum, drop_pg_enum

revision: str = "f284c22290a9"
down_revision: str | Sequence[str] | None = "cf9f30ef9574"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOURCE_KIND_VALUES = [
    "fandom_page",
    "wikidata_item",
    "wikipedia_en_page",
    "wikipedia_ja_page",
]
CONTENT_LICENSE_VALUES = ["cc_by_sa_3_0", "cc_by_sa_4_0", "cc0_1_0"]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop them (ALEM-11).
    # ``source_kind`` is shared with ``ingest_runs``, whose migration
    # reuses it without creating or dropping it.
    source_kind = create_pg_enum("source_kind", SOURCE_KIND_VALUES)
    content_license_type = create_pg_enum("content_license", CONTENT_LICENSE_VALUES)
    op.create_table(
        "sources",
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
        sa.Column("content_license", content_license_type, nullable=False),
        # TEXT, not a number: a Wikidata QID is not numeric.
        sa.Column("external_id", sa.TEXT(), nullable=False),
        sa.Column("kind", source_kind, nullable=False),
        sa.Column("retrieved_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        # BIGINT: Wikimedia revision IDs are already past 2**31.
        sa.Column("revision_id", sa.BigInteger(), nullable=True),
        sa.Column("url", sa.TEXT(), nullable=False),
        sa.CheckConstraint(
            "char_length(external_id) > 0",
            name=op.f("ck_sources_external_id_not_empty"),
        ),
        sa.CheckConstraint(
            "revision_id > 0", name=op.f("ck_sources_revision_id_positive")
        ),
        sa.CheckConstraint("url ~ '^https://'", name=op.f("ck_sources_url_format")),
        sa.PrimaryKeyConstraint("id", name=op.f("sources_pkey")),
        # The natural key (RDB-13): page IDs repeat across wikis, so it
        # is unique per kind. The loader upserts on it (SQLA-25).
        sa.UniqueConstraint(
            "kind", "external_id", name=op.f("sources_kind_external_id_key")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sources")
    drop_pg_enum("content_license", CONTENT_LICENSE_VALUES)
    drop_pg_enum("source_kind", SOURCE_KIND_VALUES)
