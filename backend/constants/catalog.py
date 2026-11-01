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
