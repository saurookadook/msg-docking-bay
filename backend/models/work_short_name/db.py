"""The ``work_short_names`` table: series tags such as ``MSG``."""

import uuid

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins.checks import not_empty
from models.mixins.db import TimestampsDB


class WorkShortNameDB(BaseDB, TimestampsDB):
    """A tag that names one work, as in ``Amuro Ray [MSG]``.

    The Gundam Wiki's ``Template:Series/Shortname`` defines them. The
    unique ``short_name`` makes each tag resolve to exactly one work; a
    table rather than a ``text[]`` on ``works``, because an array cannot
    be unique across rows (RDB-3).
    """

    short_name: Mapped[str] = mapped_column(unique=True)
    """Case-sensitive, as the wiki writes it: ``MSG II SoS``."""
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"), index=True
    )

    __table_args__ = (
        not_empty("short_name"),
        CheckConstraint("short_name = btrim(short_name)", name="short_name_trimmed"),
    )
