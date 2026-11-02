"""Fixed sets of catalog values, mirrored by enum types (PG-5)."""

from enum import StrEnum


class WorkType(StrEnum):
    """The medium of a Gundam work."""

    TV_SERIES = "tv_series"
    FILM = "film"
    OVA = "ova"
    ONA = "ona"
    MANGA = "manga"
    NOVEL = "novel"
    VIDEO_GAME = "video_game"
    OTHER = "other"
    """Documentaries, attractions (Gundam the Ride), and the like."""


class WorkRelationType(StrEnum):
    """How one work relates to another, read ``from`` → ``to``.

    ``(Zeta, MSG, sequel_of)`` reads "Zeta is a sequel of MSG".
    """

    SEQUEL_OF = "sequel_of"
    COMPILATION_OF = "compilation_of"
    """A film recut from a TV series, such as Mobile Suit Gundam I."""
    ADAPTATION_OF = "adaptation_of"
    REMAKE_OF = "remake_of"
    SIDE_STORY_OF = "side_story_of"


class SourceKind(StrEnum):
    """The kind of upstream page a catalog fact came from.

    One kind per wiki: page IDs are unique only within a wiki, and each
    wiki needs its own sync watermark in ``ingest_runs``.
    """

    FANDOM_PAGE = "fandom_page"
    """A Gundam Wiki article, keyed by its page ID."""
    WIKIDATA_ITEM = "wikidata_item"
    """A Wikidata item, keyed by its QID."""
    WIKIPEDIA_EN_PAGE = "wikipedia_en_page"
    """An English Wikipedia article, keyed by its page ID."""
    WIKIPEDIA_JA_PAGE = "wikipedia_ja_page"
    """A Japanese Wikipedia article, keyed by its page ID."""


class ContentLicense(StrEnum):
    """The terms a source's content is published under (ADR 0002)."""

    CC_BY_SA_3_0 = "cc_by_sa_3_0"
    """The Gundam Wiki on Fandom."""
    CC_BY_SA_4_0 = "cc_by_sa_4_0"
    """Wikipedia."""
    CC0_1_0 = "cc0_1_0"
    """Wikidata: public domain, no attribution required."""


class IngestRunStatus(StrEnum):
    """Where an ingest run is in its life."""

    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
