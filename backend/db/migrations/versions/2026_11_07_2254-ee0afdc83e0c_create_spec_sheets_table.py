"""Create spec_sheets table.

Revision ID: ee0afdc83e0c
Revises: 45810c544471
Create Date: 2026-11-07 22:54:09.235586+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "ee0afdc83e0c"
down_revision: str | Sequence[str] | None = "45810c544471"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Measurements are SI units in DOUBLE PRECISION (PG-2), each
    # nullable and positive: a sheet holds only what its source states.
    # ``[float]`` binds the type parameter pyright strict otherwise
    # reports as unknown; the column is the same.
    op.create_table(
        "spec_sheets",
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
        # Null for the base sheet; a named one stores only what differs.
        sa.Column("configuration", sa.TEXT(), nullable=True),
        sa.Column("empty_weight_kg", sa.DOUBLE_PRECISION[float](), nullable=True),
        sa.Column("generator_output_kw", sa.DOUBLE_PRECISION[float](), nullable=True),
        sa.Column("gross_weight_kg", sa.DOUBLE_PRECISION[float](), nullable=True),
        sa.Column("head_height_m", sa.DOUBLE_PRECISION[float](), nullable=True),
        sa.Column("max_acceleration_g", sa.DOUBLE_PRECISION[float](), nullable=True),
        sa.Column("max_speed_kmh", sa.DOUBLE_PRECISION[float](), nullable=True),
        sa.Column("mobile_suit_id", sa.Uuid(), nullable=False),
        sa.Column("overall_height_m", sa.DOUBLE_PRECISION[float](), nullable=True),
        # The infobox as read; values keep CC BY-SA terms (ADR 0002).
        sa.Column(
            "raw_infobox",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("sensor_range_m", sa.DOUBLE_PRECISION[float](), nullable=True),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("total_thrust_kg", sa.DOUBLE_PRECISION[float](), nullable=True),
        sa.Column("turn_time_s", sa.DOUBLE_PRECISION[float](), nullable=True),
        sa.CheckConstraint(
            "jsonb_typeof(raw_infobox) = 'object'",
            name=op.f("ck_spec_sheets_raw_infobox_is_object"),
        ),
        sa.CheckConstraint(
            "char_length(configuration) > 0",
            name=op.f("ck_spec_sheets_configuration_not_empty"),
        ),
        sa.CheckConstraint(
            "empty_weight_kg > 0", name=op.f("ck_spec_sheets_empty_weight_kg_positive")
        ),
        sa.CheckConstraint(
            "generator_output_kw > 0",
            name=op.f("ck_spec_sheets_generator_output_kw_positive"),
        ),
        sa.CheckConstraint(
            "gross_weight_kg > 0", name=op.f("ck_spec_sheets_gross_weight_kg_positive")
        ),
        sa.CheckConstraint(
            "head_height_m > 0", name=op.f("ck_spec_sheets_head_height_m_positive")
        ),
        sa.CheckConstraint(
            "max_acceleration_g > 0",
            name=op.f("ck_spec_sheets_max_acceleration_g_positive"),
        ),
        sa.CheckConstraint(
            "max_speed_kmh > 0", name=op.f("ck_spec_sheets_max_speed_kmh_positive")
        ),
        sa.CheckConstraint(
            "overall_height_m > 0",
            name=op.f("ck_spec_sheets_overall_height_m_positive"),
        ),
        sa.CheckConstraint(
            "sensor_range_m > 0", name=op.f("ck_spec_sheets_sensor_range_m_positive")
        ),
        sa.CheckConstraint(
            "total_thrust_kg > 0", name=op.f("ck_spec_sheets_total_thrust_kg_positive")
        ),
        sa.CheckConstraint(
            "turn_time_s > 0", name=op.f("ck_spec_sheets_turn_time_s_positive")
        ),
        sa.ForeignKeyConstraint(
            ["mobile_suit_id"],
            ["mobile_suits.id"],
            name=op.f("spec_sheets_mobile_suit_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("spec_sheets_source_id_fkey"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("spec_sheets_pkey")),
        # NULLS NOT DISTINCT (PostgreSQL 15+): otherwise two NULL
        # configurations never collide, allowing two base sheets. It
        # leads with mobile_suit_id, so that FK needs no index (RDB-18).
        sa.UniqueConstraint(
            "mobile_suit_id",
            "source_id",
            "configuration",
            name=op.f("spec_sheets_mobile_suit_id_source_id_configuration_key"),
            postgresql_nulls_not_distinct=True,
        ),
    )
    op.create_index(
        op.f("ix_spec_sheets_source_id"), "spec_sheets", ["source_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_spec_sheets_source_id"), table_name="spec_sheets")
    op.drop_table("spec_sheets")
