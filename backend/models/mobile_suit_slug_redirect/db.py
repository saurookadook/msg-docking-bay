"""The ``mobile_suit_slug_redirects`` table: old slugs of suits."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import JunctionBaseDB
from models.mixins.checks import slug_format
from models.mixins.db import CreatedAtDB


class MobileSuitSlugRedirectDB(JunctionBaseDB, CreatedAtDB):
    """A slug a suit had before its page was renamed (D2).

    A detail read that misses on ``mobile_suits.slug`` looks here, so
    old links keep working. Keyed on the old slug, so it has no
    surrogate ``id``. A current slug always wins: the loader deletes a
    redirect whose ``old_slug`` a row takes as its own.
    """

    mobile_suit_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobile_suits.id", ondelete="CASCADE"), index=True
    )
    """CASCADE: a deleted suit takes its old slugs with it."""
    old_slug: Mapped[str] = mapped_column(primary_key=True)

    __table_args__ = (slug_format("old_slug"),)
