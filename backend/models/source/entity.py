"""Entities for ``sources`` (PYD-2, PYD-3)."""

from pydantic import AwareDatetime

from constants.catalog import ContentLicense, SourceKind
from models.base.entity import BaseEntityModel
from models.mixins.entity import IdEntityMixin, TimestampsEntityMixin


class SourceEntity(BaseEntityModel, IdEntityMixin, TimestampsEntityMixin):
    """A source row, as stored."""

    content_license: ContentLicense
    external_id: str
    kind: SourceKind
    retrieved_at: AwareDatetime
    revision_id: int | None = None
    url: str


class SourceCitationEntity(BaseEntityModel):
    """The source a served fact cites, for its attribution (D6).

    Deliberately not ``SourceEntity``: ``external_id`` means nothing to
    a reader, since ``url`` already names the page, and ``id`` is not a
    public key (D5).

    ``retrieved_at`` and ``revision_id`` say which copy of the page the
    catalog holds; they say nothing about this database's row times.
    """

    content_license: ContentLicense
    kind: SourceKind
    retrieved_at: AwareDatetime
    revision_id: int | None = None
    url: str
