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


class UnitType(StrEnum):
    """The kind of mobile weapon, from the Gundam Wiki infobox ``type``.

    Only the kinds the catalog holds: the wiki's Ship, Vehicle, Weapon
    and Bit pages are out of scope.
    """

    SUIT = "suit"
    """A mobile suit, the default: the RX-78-2 Gundam."""
    ARMOR = "armor"
    """A mobile armor, such as the MA-08 Big Zam."""
    FIGHTER = "fighter"
    """A space or atmospheric fighter, such as the Core Fighter."""
    MAN_MACHINE = "man_machine"
    """A Man-Machine: a Universal Century mobile-suit precursor."""
    WORKER = "worker"
    """A civilian or construction unit, such as the Mobile Worker."""
    POD = "pod"
    """A small pod such as the Ball."""
    DOLL = "doll"
    """A Mobile Doll: an unmanned, AI-piloted unit (After Colony)."""


class MobileSuitRelationType(StrEnum):
    """How one mobile suit descends from another, read from → to.

    ``(Worker Zaku, Zaku II, variant_of)`` reads "the Worker Zaku is a
    variant of the Zaku II".
    """

    VARIANT_OF = "variant_of"
    """A modified model of the same line, such as the Zaku II Kai."""
    DEVELOPED_FROM = "developed_from"
    """A new design built on another's technology: Hi-Zack from GM."""
    UPGRADE_OF = "upgrade_of"
    """The same unit refitted, such as the Full Armor Gundam."""
    ALTERNATE_VERSION_OF = "alternate_version_of"
    """The same unit as another work depicts it: RX-78-02 and RX-78-2.

    Written in one direction only; the loader picks which.
    """


class ArmamentMount(StrEnum):
    """How a spec sheet carries an armament, from the infobox field."""

    FIXED = "fixed"
    """Built in, such as head vulcans (``fixedArmaments``)."""
    HANDHELD = "handheld"
    """Carried in hand, such as a beam rifle (``handheldArmaments``)."""
    OPTIONAL_FIXED = "optional_fixed"
    OPTIONAL_HANDHELD = "optional_handheld"


class EquipmentFit(StrEnum):
    """Whether a spec sheet's equipment is standard or optional."""

    STANDARD = "standard"
    OPTIONAL = "optional"


class MaterialUse(StrEnum):
    """What a spec sheet's material is used for."""

    ARMOR = "armor"
    FRAME = "frame"


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
