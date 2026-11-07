"""The ``spec_sheets`` table: a suit's specifications, per source."""

import uuid
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins.checks import not_empty, positive
from models.mixins.db import TimestampsDB


class SpecSheetDB(BaseDB, TimestampsDB):
    """One suit's specs as one source gives them, for one configuration.

    Typed columns in SI units rather than key-value claims (RDB-5); a
    new field is a migration that adds a column, backfilled from
    ``raw_infobox``. A second source (MAHQ, say) adds its own sheets,
    and sheets that disagree are flagged, never merged (ADR 0002).

    The base sheet has a null ``configuration``. A named one (Waverider
    mode, after an upgrade) stores only what differs: a null there
    means "same as the base sheet", and readers fill gaps from it.
    """

    configuration: Mapped[str | None]
    """Null for the base sheet; otherwise the configuration's name."""
    empty_weight_kg: Mapped[float | None]
    generator_output_kw: Mapped[float | None]
    gross_weight_kg: Mapped[float | None]
    head_height_m: Mapped[float | None]
    max_acceleration_g: Mapped[float | None]
    max_speed_kmh: Mapped[float | None]
    mobile_suit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobile_suits.id", ondelete="CASCADE")
    )
    """Not indexed on its own: it leads the unique key (RDB-18)."""
    overall_height_m: Mapped[float | None]
    raw_infobox: Mapped[dict[str, Any]] = mapped_column(
        server_default=text("'{}'::jsonb")
    )
    """The infobox fields as read, including any with no column yet.

    The values keep their article's CC BY-SA terms (ADR 0002).
    """
    sensor_range_m: Mapped[float | None]
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT"), index=True
    )
    """RESTRICT: a source still cited cannot be deleted (RDB-15)."""
    total_thrust_kg: Mapped[float | None]
    """Thrust in kilograms-force, as the wiki gives it."""
    turn_time_s: Mapped[float | None]

    __table_args__ = (
        not_empty("configuration"),
        positive("empty_weight_kg"),
        positive("generator_output_kw"),
        positive("gross_weight_kg"),
        positive("head_height_m"),
        positive("max_acceleration_g"),
        positive("max_speed_kmh"),
        positive("overall_height_m"),
        CheckConstraint(
            "jsonb_typeof(raw_infobox) = 'object'", name="raw_infobox_is_object"
        ),
        positive("sensor_range_m"),
        positive("total_thrust_kg"),
        positive("turn_time_s"),
        # NULLS NOT DISTINCT: without it, a NULL configuration never
        # collides, and a suit could have two base sheets per source.
        UniqueConstraint(
            "mobile_suit_id",
            "source_id",
            "configuration",
            postgresql_nulls_not_distinct=True,
        ),
    )
