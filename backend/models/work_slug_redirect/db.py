"""The ``work_slug_redirects`` table: old slugs of renamed works."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import JunctionBaseDB
from models.mixins.checks import slug_format
from models.mixins.db import CreatedAtDB


class WorkSlugRedirectDB(JunctionBaseDB, CreatedAtDB):
    """A slug a work had before its page was renamed (D2).

    A detail read that misses on ``works.slug`` looks here, so old
    links keep working. Keyed on the old slug, so it has no surrogate
    ``id``. A current slug always wins: the loader deletes a redirect
    whose ``old_slug`` a row takes as its own.
    """

    old_slug: Mapped[str] = mapped_column(primary_key=True)
    work_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("works.id", ondelete="CASCADE"), index=True
    )
    """CASCADE: a deleted work takes its old slugs with it."""

    __table_args__ = (slug_format("old_slug"),)
