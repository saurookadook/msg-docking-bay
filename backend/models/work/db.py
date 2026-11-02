"""The ``works`` table: every Gundam series, film, OVA, and game."""

import uuid
from datetime import date

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from constants.catalog import WorkType
from constants.db_types import WORK_TYPE_DB_TYPE
from db.base_db import BaseDB
from models.mixins.checks import not_empty, not_own_parent, slug_format
from models.mixins.db import TimestampsDB


class WorkDB(BaseDB, TimestampsDB):
    """A work, seeded from Wikidata and linked to the Gundam Wiki.

    Seasons point at their series through ``parent_work_id``, so the
    Witch from Mercury's two Wikidata season items roll up to one work.
    """

    anilist_id: Mapped[int | None] = mapped_column(unique=True)
    ann_id: Mapped[int | None] = mapped_column(unique=True)
    """The Anime News Network Encyclopedia ID."""
    continuity_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("continuities.id", ondelete="SET NULL"), index=True
    )
    """Null for crossovers that span timelines, such as G Generation."""
    end_date: Mapped[date | None]
    fandom_page_title: Mapped[str | None] = mapped_column(unique=True)
    parent_work_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("works.id", ondelete="SET NULL"), index=True
    )
    """The series a season or part belongs to."""
    slug: Mapped[str] = mapped_column(unique=True)
    start_date: Mapped[date | None]
    """The premiere or release date; null when not yet known."""
    title: Mapped[str]
    """Not unique: a TV series and a game can share a title."""
    title_ja: Mapped[str | None]
    wikidata_qid: Mapped[str | None] = mapped_column(unique=True)
    work_type: Mapped[WorkType] = mapped_column(WORK_TYPE_DB_TYPE)

    __table_args__ = (
        CheckConstraint("anilist_id > 0", name="anilist_id_positive"),
        CheckConstraint("ann_id > 0", name="ann_id_positive"),
        CheckConstraint("end_date >= start_date", name="end_after_start"),
        not_empty("fandom_page_title"),
        not_own_parent("parent_work_id"),
        slug_format(),
        not_empty("title"),
        not_empty("title_ja"),
        CheckConstraint("wikidata_qid ~ '^Q[0-9]+$'", name="wikidata_qid_format"),
    )
