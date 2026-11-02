"""Add source_id to work_relations.

Revision ID: 71aaa31e79ec
Revises: b9dcf7885d38
Create Date: 2026-11-02 02:19:15.347076+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "71aaa31e79ec"
down_revision: str | Sequence[str] | None = "b9dcf7885d38"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Every edge cites the page it was read from (ADR 0002). A separate
    # revision, because ``sources`` is created after ``work_relations``.
    # NOT NULL with no default is safe: no loader has written edges yet.
    op.add_column("work_relations", sa.Column("source_id", sa.Uuid(), nullable=False))
    op.create_index(
        op.f("ix_work_relations_source_id"),
        "work_relations",
        ["source_id"],
        unique=False,
    )
    # RESTRICT: a source that an edge still cites cannot be deleted.
    op.create_foreign_key(
        op.f("work_relations_source_id_fkey"),
        "work_relations",
        "sources",
        ["source_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("work_relations_source_id_fkey"), "work_relations", type_="foreignkey"
    )
    op.drop_index(op.f("ix_work_relations_source_id"), table_name="work_relations")
    op.drop_column("work_relations", "source_id")
