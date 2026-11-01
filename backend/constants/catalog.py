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
