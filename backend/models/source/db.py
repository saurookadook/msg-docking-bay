"""The ``sources`` table: one row per upstream page (ADR 0002)."""

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from constants.catalog import ContentLicense, SourceKind
from constants.db_types import CONTENT_LICENSE_DB_TYPE, SOURCE_KIND_DB_TYPE
from db.base_db import BaseDB
from models.mixins.checks import not_empty
from models.mixins.db import TimestampsDB


class SourceDB(BaseDB, TimestampsDB):
    """An upstream page that spec sheets, edges and appearances cite.

    Re-ingesting a page updates its row in place: ``revision_id`` and
    ``retrieved_at`` always describe the copy the catalog now holds.
    """

    content_license: Mapped[ContentLicense] = mapped_column(CONTENT_LICENSE_DB_TYPE)
    """Which terms apply to text kept from this page (ADR 0002)."""
    external_id: Mapped[str]
    """The page's ID upstream: a Fandom or Wikipedia page ID, or a QID.

    Unique per ``kind`` only, since page IDs repeat across wikis.
    """
    kind: Mapped[SourceKind] = mapped_column(SOURCE_KIND_DB_TYPE)
    retrieved_at: Mapped[datetime]
    """When the loaded copy was fetched; for a dump, the dump's date."""
    revision_id: Mapped[int | None] = mapped_column(BigInteger)
    """The upstream revision loaded; null when the source has none."""
    url: Mapped[str]
    """The canonical page URL, shown with the attribution."""

    __table_args__ = (
        not_empty("external_id"),
        CheckConstraint("revision_id > 0", name="revision_id_positive"),
        CheckConstraint("url ~ '^https://'", name="url_format"),
        UniqueConstraint("kind", "external_id"),
    )
