"""Create ingest_runs table.

Revision ID: b9dcf7885d38
Revises: f284c22290a9
Create Date: 2026-11-02 01:39:52.315022+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from db.migrations.alembic_utilities import (
    create_pg_enum,
    drop_pg_enum,
    existing_pg_enum,
)

revision: str = "b9dcf7885d38"
down_revision: str | Sequence[str] | None = "f284c22290a9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INGEST_RUN_STATUS_VALUES = ["running", "succeeded", "failed"]
SOURCE_KIND_VALUES = [
    "fandom_page",
    "wikidata_item",
    "wikipedia_en_page",
    "wikipedia_ja_page",
]


def upgrade() -> None:
    """Upgrade schema."""
    # Created explicitly so downgrade() can drop it (ALEM-11).
    ingest_run_status = create_pg_enum("ingest_run_status", INGEST_RUN_STATUS_VALUES)
    # ``source_kind`` belongs to the sources migration (f284c22290a9),
    # which creates and drops it; this one only references it.
    source_kind = existing_pg_enum("source_kind", SOURCE_KIND_VALUES)
    op.create_table(
        "ingest_runs",
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
        sa.Column("error_count", sa.Integer(), server_default="0", nullable=False),
        # SQLSTATEs and constraint names only, never row data.
        sa.Column("error_summary", sa.TEXT(), nullable=True),
        sa.Column("finished_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("pages_seen", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rows_written", sa.Integer(), server_default="0", nullable=False),
        sa.Column("source_kind", source_kind, nullable=False),
        sa.Column(
            "started_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "status",
            ingest_run_status,
            server_default="running",
            nullable=False,
        ),
        # Not the current watermark: that is the latest succeeded run's,
        # computed rather than stored (RDB-1).
        sa.Column("watermark_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint(
            "error_count >= 0", name=op.f("ck_ingest_runs_error_count_not_negative")
        ),
        sa.CheckConstraint(
            "char_length(error_summary) > 0",
            name=op.f("ck_ingest_runs_error_summary_not_empty"),
        ),
        sa.CheckConstraint(
            "finished_at >= started_at",
            name=op.f("ck_ingest_runs_finished_after_started"),
        ),
        # A run has a finish time exactly when it is no longer running,
        # so a status and its timestamp cannot disagree (RDB-14).
        sa.CheckConstraint(
            "(status = 'running') = (finished_at IS NULL)",
            name=op.f("ck_ingest_runs_finished_unless_running"),
        ),
        sa.CheckConstraint(
            "pages_seen >= 0", name=op.f("ck_ingest_runs_pages_seen_not_negative")
        ),
        sa.CheckConstraint(
            "rows_written >= 0", name=op.f("ck_ingest_runs_rows_written_not_negative")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("ingest_runs_pkey")),
    )
    # Serves "the latest succeeded run for a source kind", which is how
    # the loader finds its watermark.
    op.create_index(
        "ix_ingest_runs_source_kind_status_started_at",
        "ingest_runs",
        ["source_kind", "status", "started_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_ingest_runs_source_kind_status_started_at", table_name="ingest_runs"
    )
    op.drop_table("ingest_runs")
    drop_pg_enum("ingest_run_status", INGEST_RUN_STATUS_VALUES)
