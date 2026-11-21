"""Entities for ``sources`` (PYD-2, PYD-3)."""

from collections.abc import Callable
from typing import Final
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import AwareDatetime, computed_field

from constants.catalog import LICENSES, ContentLicense, SourceKind
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


def _with_oldid(url: str, revision_id: int) -> str:
    """Add ``oldid`` to a MediaWiki page URL, keeping its query.

    ``https://gundam.fandom.com/?curid=2034`` keeps its ``curid``.
    """
    parts = urlsplit(url)
    query = [*parse_qsl(parts.query), ("oldid", str(revision_id))]
    return urlunsplit(parts._replace(query=urlencode(query)))


def _wikidata_revision(url: str, revision_id: int) -> str:
    """Link a Wikidata item's revision through ``index.php``.

    ``https://www.wikidata.org/wiki/Q1134906`` becomes
    ``https://www.wikidata.org/w/index.php?title=Q1134906&oldid=N``.
    """
    parts = urlsplit(url)
    qid = parts.path.rsplit("/", 1)[-1]
    query = urlencode({"title": qid, "oldid": str(revision_id)})
    return urlunsplit(parts._replace(path="/w/index.php", query=query))


_REVISION_URL_BUILDERS: Final[dict[SourceKind, Callable[[str, int], str]]] = {
    SourceKind.FANDOM_PAGE: _with_oldid,
    SourceKind.WIKIDATA_ITEM: _wikidata_revision,
    SourceKind.WIKIPEDIA_EN_PAGE: _with_oldid,
    SourceKind.WIKIPEDIA_JA_PAGE: _with_oldid,
}
"""How each kind of source links one revision (PY-35, D6)."""


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

    @computed_field
    @property
    def license_name(self) -> str:
        """The license's name, such as ``CC BY-SA 3.0`` (D6)."""
        return LICENSES[self.content_license].name

    @computed_field
    @property
    def license_url(self) -> str:
        """The license's deed URL (D6)."""
        return LICENSES[self.content_license].url

    @computed_field
    @property
    def revision_url(self) -> str | None:
        """A permalink to the revision the catalog holds, or ``None``.

        Share-alike attribution points at the version used, not the
        live page (D6). ``None`` when no revision was recorded.
        """
        if self.revision_id is None:
            return None
        return _REVISION_URL_BUILDERS[self.kind](self.url, self.revision_id)
