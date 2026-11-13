"""The ``organizations`` table: factions, militaries and companies."""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_db import BaseDB
from models.mixins.checks import not_empty, not_own_parent, slug_format
from models.mixins.db import TimestampsDB


class OrganizationDB(BaseDB, TimestampsDB):
    """An organization, such as the EFSF or Anaheim Electronics.

    One row however many series it appears in; membership lives in
    ``organization_appearances``. Sub-units nest through
    ``parent_organization_id`` (RDB-7). Revisit if a unit changes
    hands across eras: that needs an ``organization_relations`` edge
    table, as mobile suits have.
    """

    fandom_page_title: Mapped[str | None] = mapped_column(unique=True)
    """The Gundam Wiki page title; null when it has no page."""
    name: Mapped[str]
    """Not unique: organizations are told apart by ``slug``."""
    parent_organization_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), index=True
    )
    """The organization this one is a unit of: Titans → EFF."""
    slug: Mapped[str] = mapped_column(unique=True)

    __table_args__ = (
        not_empty("fandom_page_title"),
        not_empty("name"),
        not_own_parent("parent_organization_id"),
        slug_format(),
    )
