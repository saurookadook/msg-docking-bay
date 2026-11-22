"""Seed a small, real slice of the catalog into a dev or test database.

Four suits (RX-78-2, RX-78-02, RX-78F00 and the MS-06F Zaku II), the
five works they appear in, the Universal Century, the two Amuros who
pilot the Gundams, three organizations and three designers named in
the suits' infoboxes, the parts those infoboxes list (a representative
subset: no sub-items or per-work tags), and the Gundam Wiki pages each
fact came from.
Every value was read by hand from the Gundam Wiki's
``gundam_pages_current.xml.7z`` dump of 2026-11-15
(``ingest/data/dumps/``, SHA-256 ``89a91167…``). The frontend's Mirage
fixtures (``frontend/src/__mocks__/``) hold a second copy of the
same rows; change both together.

Every row is written through a facade's ``create_or_update``, so a
rerun changes nothing and leaves every ``updated_at`` alone. The real
load is the Phase 3a ingest, so this refuses to run outside ``dev`` and
``test``, and after a completed ingest run unless given ``--force``.

Run it with ``moon run backend:seed-dev``, or in the backend container
with ``python -m scripts.seed_dev``.
"""

import argparse
import logging
import sys
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Any, Final, NamedTuple, Protocol, TypedDict
from urllib.parse import quote

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from config.env_vars import EnvVarManager
from constants.catalog import (
    ArmamentMount,
    ContentLicense,
    EquipmentFit,
    IngestRunStatus,
    MaterialUse,
    MobileSuitOrganizationRole,
    MobileSuitRelationType,
    SourceKind,
    UnitType,
    WorkRelationType,
    WorkType,
)
from db.db_session_manager import DBSessionManager
from models.armament.facade import ArmamentFacade
from models.character.facade import CharacterFacade
from models.continuity.facade import ContinuityFacade
from models.equipment.facade import EquipmentFacade
from models.ingest_run.db import IngestRunDB
from models.material.facade import MaterialFacade
from models.mechanical_designer.facade import MechanicalDesignerFacade
from models.mobile_suit.facade import MobileSuitFacade
from models.mobile_suit_designer.facade import MobileSuitDesignerFacade
from models.mobile_suit_organization.facade import MobileSuitOrganizationFacade
from models.mobile_suit_pilot.facade import MobileSuitPilotFacade
from models.organization.facade import OrganizationFacade
from models.powerplant.facade import PowerplantFacade
from models.source.facade import SourceFacade
from models.spec_sheet_armament.facade import SpecSheetArmamentFacade
from models.spec_sheet_equipment.facade import SpecSheetEquipmentFacade
from models.spec_sheet_material.facade import SpecSheetMaterialFacade
from models.spec_sheet_powerplant.facade import SpecSheetPowerplantFacade
from models.work.facade import WorkFacade
from utils.logging.init import init_logging

if TYPE_CHECKING:
    from models.spec_sheet.entity import SpecSheetPartKind

DESCRIPTION: Final = "Seed a small, real slice of the catalog for development."

RETRIEVED_AT: Final = datetime(2026, 11, 15, 23, 32, 58, tzinfo=UTC)
"""The dump's ``Last-Modified``: when these page copies were made."""

SEEDABLE_ENVIRONMENTS: Final = frozenset({"dev", "test"})

logger = logging.getLogger(__name__)


class SeedRefusedError(Exception):
    """The database is not one this script may write to."""


class CharacterRow(TypedDict):
    """A seeded character, named after their Gundam Wiki page."""

    name: str
    name_ja: str
    page: str
    slug: str
    works: list[str]


class OrganizationRow(TypedDict):
    """A seeded organization; its name is its page's title."""

    page: str
    slug: str
    works: list[str]


class MechanicalDesignerRow(TypedDict):
    """A seeded designer; ``page`` is null when they have none."""

    name: str
    name_ja: str | None
    page: str | None
    slug: str


class PilotRow(NamedTuple):
    """A character piloting a suit, in a work or in none."""

    character: str
    suit: str
    work: str | None


class SuitOrganizationRow(NamedTuple):
    """An organization's role for a suit, in a work or in none."""

    suit: str
    organization: str
    role: MobileSuitOrganizationRole
    work: str | None


class PartRow(NamedTuple):
    """A part as the infobox names it.

    ``page_id`` is set only when the name is the title of the part's own
    article; a title that redirects to a list section is no page of its
    own, so such a part has neither title nor page ID.
    """

    name: str
    slug: str
    page_id: int | None = None


class ArmamentListingRow(NamedTuple):
    """An armament on a suit's base sheet, with its infobox count."""

    suit: str
    armament: str
    mount: ArmamentMount
    quantity_min: int | None = None
    quantity_max: int | None = None
    note: str | None = None


class EquipmentListingRow(NamedTuple):
    """An item of equipment on a suit's base sheet."""

    suit: str
    equipment: str
    fit: EquipmentFit
    note: str | None = None


class MaterialListingRow(NamedTuple):
    """A material on a suit's base sheet."""

    suit: str
    material: str
    material_use: MaterialUse
    note: str | None = None


class PowerplantListingRow(NamedTuple):
    """A powerplant on a suit's base sheet, with its infobox count."""

    suit: str
    powerplant: str
    quantity_min: int | None = None
    quantity_max: int | None = None
    note: str | None = None


@dataclass(frozen=True)
class SeededIds:
    """The IDs the people rows point at, by slug or page title."""

    sources: Mapping[str, uuid.UUID]
    """By page title."""
    suits: Mapping[str, uuid.UUID]
    suit_sources: Mapping[str, uuid.UUID]
    """The source of each suit's page, by suit slug."""
    works: Mapping[str, uuid.UUID]


def fandom_url(title: str) -> str:
    """Return a Gundam Wiki article's URL, as MediaWiki links it."""
    return "https://gundam.fandom.com/wiki/" + quote(
        title.replace(" ", "_"), safe=":/,!()'"
    )


PAGES: Final[dict[str, tuple[int, int]]] = {
    "Mobile Suit Gundam": (10, 665644),
    "Mobile Suit Gundam I": (78840, 703163),
    "Mobile Suit Gundam: The Origin": (96900, 705008),
    "Mobile Suit Gundam: The Origin Advent of the Red Comet": (105029, 693655),
    "It Moves? Gundam, Follow Your Dreams!": (114772, 637504),
    "RX-78-2 Gundam": (2586, 707889),
    "RX-78-02 Gundam": (27439, 707929),
    "RX-78F00 Gundam": (117454, 707440),
    "MS-06F Zaku II": (7305, 706593),
    "Amuro Ray": (2461, 705278),
    "Amuro Ray (Origin)": (84207, 694015),
    "Earth Federation": (2711, 685169),
    "Principality of Zeon": (147, 701574),
    "Zeonic": (13138, 700584),
    "Kunio Okawara": (2701, 705027),
    "Hajime Katoki": (2378, 674807),
}
"""Each article's page ID and the revision the dump holds."""

WORKS: Final[list[dict[str, Any]]] = [
    {
        "end_date": date(1980, 1, 26),
        "page": "Mobile Suit Gundam",
        "slug": "mobile-suit-gundam",
        "start_date": date(1979, 4, 7),
        "title_ja": "機動戦士ガンダム",
        "universal_century": True,
        "work_type": WorkType.TV_SERIES,
    },
    {
        "end_date": None,
        "page": "Mobile Suit Gundam I",
        "slug": "mobile-suit-gundam-i",
        "start_date": date(1981, 3, 4),
        "title_ja": "劇場版 機動戦士ガンダム",
        "universal_century": True,
        "work_type": WorkType.FILM,
    },
    {
        "end_date": date(2018, 5, 5),
        "page": "Mobile Suit Gundam: The Origin",
        "slug": "mobile-suit-gundam-the-origin",
        "start_date": date(2015, 2, 28),
        "title_ja": "機動戦士ガンダム THE ORIGIN",
        "universal_century": True,
        "work_type": WorkType.OVA,
    },
    {
        "end_date": date(2019, 8, 11),
        "page": "Mobile Suit Gundam: The Origin Advent of the Red Comet",
        "slug": "mobile-suit-gundam-the-origin-advent-of-the-red-comet",
        "start_date": date(2019, 4, 29),
        "title_ja": "機動戦士ガンダム THE ORIGIN 前夜 赤い彗星",
        "universal_century": True,
        "work_type": WorkType.TV_SERIES,
    },
    {
        # A documentary; the wiki gives its era as "Not Applicable".
        "end_date": date(2021, 3, 30),
        "page": "It Moves? Gundam, Follow Your Dreams!",
        "slug": "it-moves-gundam-follow-your-dreams",
        "start_date": date(2020, 3, 23),
        # The wiki's full-width punctuation, kept as written.
        "title_ja": "動くのか？ガンダム 夢への挑戦！",  # noqa: RUF001
        "universal_century": False,
        "work_type": WorkType.OTHER,
    },
]

WORK_RELATIONS: Final[list[tuple[str, WorkRelationType, str]]] = [
    ("mobile-suit-gundam-i", WorkRelationType.COMPILATION_OF, "mobile-suit-gundam"),
    (
        "mobile-suit-gundam-the-origin-advent-of-the-red-comet",
        WorkRelationType.COMPILATION_OF,
        "mobile-suit-gundam-the-origin",
    ),
]
"""``(from, type, to)``, each cited to the ``from`` work's page."""

SUITS: Final[list[dict[str, Any]]] = [
    {
        "model_number": "RX-78-2",
        "name": "Gundam",
        "name_ja": "ガンダム",
        "page": "RX-78-2 Gundam",
        "slug": "rx-78-2-gundam",
        "universal_century": True,
    },
    {
        "model_number": "RX-78-02",
        "name": "Gundam",
        "name_ja": "ガンダム",
        "page": "RX-78-02 Gundam",
        "slug": "rx-78-02-gundam",
        "universal_century": True,
    },
    {
        # The life-size statue at Gundam Factory Yokohama: no era.
        "model_number": "RX-78F00",
        "name": "Gundam",
        "name_ja": "ガンダム",
        "page": "RX-78F00 Gundam",
        "slug": "rx-78f00-gundam",
        "universal_century": False,
    },
    {
        "model_number": "MS-06F",
        "name": "Zaku II",
        "name_ja": "量産型ザクII",
        "page": "MS-06F Zaku II",
        "slug": "ms-06f-zaku-ii",
        "universal_century": True,
    },
]

SPEC_SHEETS: Final[list[dict[str, Any]]] = [
    {
        "configuration": None,
        "empty_weight_kg": 43400.0,
        "generator_output_kw": 1380.0,
        "gross_weight_kg": 60000.0,
        "head_height_m": 18.0,
        "max_acceleration_g": 0.93,
        "max_speed_kmh": 165.0,
        "raw_infobox": {
            "emptyweight": "43.4",
            "headheight": "18.0",
            "maxaccel": "0.93",
            "maxspeed": "165",
            "poweroutput": "1380",
            # The infobox text as written, multiplication signs and all.
            "propRocketThrusters": "2 × 24000, 4 × 1870",  # noqa: RUF001
            "sensorrange": "5700",
            "turntime": "1.5",
            "weight": "60.0",
        },
        "sensor_range_m": 5700.0,
        "suit": "rx-78-2-gundam",
        "total_thrust_kg": 55480.0,
        "turn_time_s": 1.5,
    },
    {
        # The infobox gives "1.1~after magnet coating upgrade".
        "configuration": "Magnet Coating",
        "raw_infobox": {"turntime": "1.1~after magnet coating upgrade"},
        "suit": "rx-78-2-gundam",
        "turn_time_s": 1.1,
    },
    {
        "configuration": None,
        "head_height_m": 18.0,
        "raw_infobox": {"headheight": "18.0"},
        "suit": "rx-78-02-gundam",
    },
    {
        "configuration": None,
        "gross_weight_kg": 25000.0,
        "head_height_m": 18.0,
        "raw_infobox": {"headheight": "18", "weight": "25"},
        "suit": "rx-78f00-gundam",
    },
    {
        "configuration": None,
        "empty_weight_kg": 58100.0,
        "generator_output_kw": 951.0,
        "gross_weight_kg": 73300.0,
        "head_height_m": 17.5,
        "max_acceleration_g": 0.59,
        "max_speed_kmh": 88.0,
        "raw_infobox": {
            "emptyweight": "58.1",
            "headheight": "17.5",
            "maxaccel": "0.59",
            "maxspeed": "88",
            "poweroutput": "951",
            # The infobox text as written, multiplication signs and all.
            "propRocketThrusters": "2 × 20500, 2 × 1000",  # noqa: RUF001
            "sensorrange": "3200",
            "turntime": "1.7",
            "weight": "73.3",
        },
        "sensor_range_m": 3200.0,
        "suit": "ms-06f-zaku-ii",
        "total_thrust_kg": 43000.0,
        "turn_time_s": 1.7,
    },
]
"""In SI units: weights from tonnes, thrusts summed per suit."""

SUIT_RELATIONS: Final[list[tuple[str, MobileSuitRelationType, str]]] = [
    ("rx-78-02-gundam", MobileSuitRelationType.ALTERNATE_VERSION_OF, "rx-78-2-gundam"),
    ("rx-78f00-gundam", MobileSuitRelationType.ALTERNATE_VERSION_OF, "rx-78-2-gundam"),
]
"""``(from, type, to)``, each cited to the ``from`` suit's page."""

APPEARANCES: Final[list[dict[str, Any]]] = [
    {
        "first_episode": 1,
        "is_debut": True,
        "last_episode": 43,
        "suit": "rx-78-2-gundam",
        "work": "mobile-suit-gundam",
    },
    {"is_debut": False, "suit": "rx-78-2-gundam", "work": "mobile-suit-gundam-i"},
    # The article says the RX-78-02 debuts in the manga, which the seed
    # leaves out, so neither of these is its debut.
    {
        "is_debut": False,
        "suit": "rx-78-02-gundam",
        "work": "mobile-suit-gundam-the-origin",
    },
    {
        "is_debut": False,
        "suit": "rx-78-02-gundam",
        "work": "mobile-suit-gundam-the-origin-advent-of-the-red-comet",
    },
    {
        "is_debut": True,
        "suit": "rx-78f00-gundam",
        "work": "it-moves-gundam-follow-your-dreams",
    },
    {"is_debut": True, "suit": "ms-06f-zaku-ii", "work": "mobile-suit-gundam"},
    {"is_debut": False, "suit": "ms-06f-zaku-ii", "work": "mobile-suit-gundam-i"},
]
"""Each cited to the suit's page, whose infobox lists the works."""

SUIT_SLUG_REDIRECTS: Final[dict[str, str]] = {"rx-78-2": "rx-78-2-gundam"}
"""The wiki's ``RX-78-2`` redirect page, as an old slug (D2)."""

WORK_SLUG_REDIRECTS: Final[dict[str, str]] = {"msg": "mobile-suit-gundam"}
"""The wiki's ``MSG`` redirect page, as an old slug (D2)."""

CHARACTERS: Final[list[CharacterRow]] = [
    {
        "name": "Amuro Ray",
        "name_ja": "アムロ・レイ",
        "page": "Amuro Ray",
        "slug": "amuro-ray",
        "works": ["mobile-suit-gundam", "mobile-suit-gundam-i"],
    },
    {
        # The Origin's Amuro has a page of his own, under the same name.
        "name": "Amuro Ray",
        "name_ja": "アムロ・レイ",
        "page": "Amuro Ray (Origin)",
        "slug": "amuro-ray-origin",
        "works": ["mobile-suit-gundam-the-origin"],
    },
]
"""Each ``works`` entry is a seeded work in the page's ``series``."""

ORGANIZATIONS: Final[list[OrganizationRow]] = [
    {
        "page": "Earth Federation",
        "slug": "earth-federation",
        "works": ["mobile-suit-gundam", "mobile-suit-gundam-i"],
    },
    {
        "page": "Principality of Zeon",
        "slug": "principality-of-zeon",
        "works": ["mobile-suit-gundam", "mobile-suit-gundam-i"],
    },
    # Its page lists no seeded work.
    {"page": "Zeonic", "slug": "zeonic", "works": []},
]
"""Named after their pages; none has a parent on the wiki."""

MECHANICAL_DESIGNERS: Final[list[MechanicalDesignerRow]] = [
    {
        "name": "Hajime Katoki",
        "name_ja": "カトキハジメ",
        "page": "Hajime Katoki",
        "slug": "hajime-katoki",
    },
    {
        # The page's spacing, kept as written.
        "name": "Kunio Okawara",
        "name_ja": "大河原 邦男",
        "page": "Kunio Okawara",
        "slug": "kunio-okawara",
    },
    # Credited on the RX-78F00 page, but with no page of his own.
    {
        "name": "Masaki Kawahara",
        "name_ja": None,
        "page": None,
        "slug": "masaki-kawahara",
    },
]

PILOTS: Final[list[PilotRow]] = [
    PilotRow("amuro-ray", "rx-78-2-gundam", "mobile-suit-gundam"),
    # The infobox gives this pairing no work.
    PilotRow("amuro-ray-origin", "rx-78-02-gundam", None),
]
"""Each cited to the suit's page."""

SUIT_ORGANIZATIONS: Final[list[SuitOrganizationRow]] = [
    SuitOrganizationRow(
        "rx-78-2-gundam",
        "earth-federation",
        MobileSuitOrganizationRole.MANUFACTURER,
        None,
    ),
    SuitOrganizationRow(
        "ms-06f-zaku-ii", "zeonic", MobileSuitOrganizationRole.MANUFACTURER, None
    ),
    SuitOrganizationRow(
        "ms-06f-zaku-ii",
        "principality-of-zeon",
        MobileSuitOrganizationRole.OPERATOR,
        None,
    ),
]
"""Each cited to the suit's page; none is tagged with a work."""

SUIT_DESIGNERS: Final[list[tuple[str, str]]] = [
    ("rx-78-2-gundam", "kunio-okawara"),
    # Okawara for the manga, Katoki for the anime.
    ("rx-78-02-gundam", "kunio-okawara"),
    ("rx-78-02-gundam", "hajime-katoki"),
    ("rx-78f00-gundam", "masaki-kawahara"),
    ("ms-06f-zaku-ii", "kunio-okawara"),
]
"""``(suit, designer)``, each cited to the suit's page."""

CHARACTER_SLUG_REDIRECTS: Final[dict[str, str]] = {"amuro": "amuro-ray"}
"""The wiki's ``Amuro`` redirect page, as an old slug (D2)."""

ORGANIZATION_SLUG_REDIRECTS: Final[dict[str, str]] = {
    "earth-federation-universal-century": "earth-federation"
}
"""The wiki's ``Earth Federation (Universal Century)`` redirect page."""

MECHANICAL_DESIGNER_SLUG_REDIRECTS: Final[dict[str, str]] = {
    "katoki-hajime": "hajime-katoki"
}
"""The wiki's ``Katoki Hajime`` redirect page, as an old slug (D2)."""


ARMAMENTS: Final[list[PartRow]] = [
    PartRow("120mm Machine Gun", "120mm-machine-gun"),
    PartRow("3-tube Missile Pod", "3-tube-missile-pod"),
    PartRow("60mm Vulcan Gun", "60mm-vulcan-gun"),
    PartRow(
        "BLASH-XHB-L-03/N-STD 380mm Hyper Bazooka",
        "blash-xhb-l-03-n-std-380mm-hyper-bazooka",
    ),
    PartRow("BOWA-XBR-M-79-07G Beam Rifle", "bowa-xbr-m-79-07g-beam-rifle"),
    # NOTE: its wiki title redirects to a list of weapons.
    PartRow("Beam Rifle", "beam-rifle"),
    PartRow("Beam Saber", "beam-saber", page_id=2405),
    PartRow("Heat Hawk", "heat-hawk"),
    PartRow("MMP-80 90mm Machine Gun", "mmp-80-90mm-machine-gun"),
    PartRow("Shoulder Cannon", "shoulder-cannon"),
    PartRow("Shoulder Shield", "shoulder-shield"),
    PartRow("Vulcan Gun", "vulcan-gun", page_id=3606),
]

EQUIPMENT: Final[list[PartRow]] = [
    PartRow("Core Block System", "core-block-system", page_id=8697),
    PartRow("Magnet Coating", "magnet-coating"),
]

MATERIALS: Final[list[PartRow]] = [
    PartRow("Luna Titanium Alloy", "luna-titanium-alloy", page_id=3877),
    PartRow("Super Hard Steel Alloy", "super-hard-steel-alloy"),
]

POWERPLANTS: Final[list[PartRow]] = [
    # NOTE: its wiki title redirects to a section of the technology
    # page.
    PartRow(
        "Minovsky Ultracompact Fusion Reactor", "minovsky-ultracompact-fusion-reactor"
    ),
]

SHEET_ARMAMENTS: Final[list[ArmamentListingRow]] = [
    ArmamentListingRow("rx-78-2-gundam", "60mm-vulcan-gun", ArmamentMount.FIXED, 2, 2),
    ArmamentListingRow(
        "rx-78-2-gundam", "bowa-xbr-m-79-07g-beam-rifle", ArmamentMount.HANDHELD
    ),
    ArmamentListingRow(
        "rx-78-2-gundam",
        "beam-saber",
        ArmamentMount.HANDHELD,
        2,
        2,
        note="2 x Beam Javelin",
    ),
    ArmamentListingRow(
        "rx-78-2-gundam",
        "blash-xhb-l-03-n-std-380mm-hyper-bazooka",
        ArmamentMount.OPTIONAL_HANDHELD,
        1,
        2,
    ),
    ArmamentListingRow("rx-78-02-gundam", "vulcan-gun", ArmamentMount.FIXED, 2, 2),
    ArmamentListingRow("rx-78-02-gundam", "beam-saber", ArmamentMount.FIXED, 1, 2),
    ArmamentListingRow("rx-78-02-gundam", "beam-rifle", ArmamentMount.HANDHELD),
    ArmamentListingRow(
        "rx-78-02-gundam", "shoulder-cannon", ArmamentMount.OPTIONAL_FIXED
    ),
    ArmamentListingRow("ms-06f-zaku-ii", "shoulder-shield", ArmamentMount.FIXED),
    ArmamentListingRow("ms-06f-zaku-ii", "120mm-machine-gun", ArmamentMount.HANDHELD),
    ArmamentListingRow("ms-06f-zaku-ii", "heat-hawk", ArmamentMount.HANDHELD),
    ArmamentListingRow(
        "ms-06f-zaku-ii", "3-tube-missile-pod", ArmamentMount.OPTIONAL_FIXED, 2, 2
    ),
    ArmamentListingRow(
        "ms-06f-zaku-ii", "mmp-80-90mm-machine-gun", ArmamentMount.OPTIONAL_HANDHELD
    ),
]
"""A count of two sets both bounds, ``1-2`` a range, none neither."""

SHEET_EQUIPMENT: Final[list[EquipmentListingRow]] = [
    EquipmentListingRow("rx-78-2-gundam", "core-block-system", EquipmentFit.STANDARD),
    EquipmentListingRow(
        "rx-78-2-gundam",
        "magnet-coating",
        EquipmentFit.STANDARD,
        note="field upgrade",
    ),
    EquipmentListingRow(
        "rx-78-02-gundam", "core-block-system", EquipmentFit.STANDARD, note="refit"
    ),
]

SHEET_MATERIALS: Final[list[MaterialListingRow]] = [
    MaterialListingRow("rx-78-2-gundam", "luna-titanium-alloy", MaterialUse.ARMOR),
    MaterialListingRow("rx-78-02-gundam", "luna-titanium-alloy", MaterialUse.ARMOR),
    MaterialListingRow("ms-06f-zaku-ii", "super-hard-steel-alloy", MaterialUse.ARMOR),
]

SHEET_POWERPLANTS: Final[list[PowerplantListingRow]] = [
    PowerplantListingRow("rx-78-2-gundam", "minovsky-ultracompact-fusion-reactor"),
    PowerplantListingRow("rx-78-02-gundam", "minovsky-ultracompact-fusion-reactor"),
]
"""The Zaku II's infobox names none; the RX-78F00's lists no parts."""


def check_environment() -> None:
    """Refuse a database outside dev and test.

    Raises:
        SeedRefusedError: when ``ENVIRONMENT`` is anything else.
    """
    environment = EnvVarManager().env_vars.environment
    if environment not in SEEDABLE_ENVIRONMENTS:
        raise SeedRefusedError(f"Refusing to seed in the '{environment}' environment")


def check_no_completed_ingest(db_session: Session) -> None:
    """Refuse a database that a real ingest has loaded.

    Raises:
        SeedRefusedError: when ``ingest_runs`` has a succeeded run.
    """
    loaded = db_session.scalar(
        select(exists().where(IngestRunDB.status == IngestRunStatus.SUCCEEDED))
    )
    if loaded:
        raise SeedRefusedError(
            "Refusing to seed over a completed ingest run; pass --force to seed anyway"
        )


def seed(db_session: Session) -> None:
    """Upsert every seed row, parents before the rows that cite them.

    Does not commit: the caller owns the transaction (SQLA-15).
    """
    sources = SourceFacade(db_session=db_session)
    source_ids: dict[str, uuid.UUID] = {}
    for title, (page_id, revision_id) in PAGES.items():
        source = sources.create_or_update(
            payload={
                "content_license": ContentLicense.CC_BY_SA_3_0,
                "external_id": str(page_id),
                "kind": SourceKind.FANDOM_PAGE,
                "retrieved_at": RETRIEVED_AT,
                "revision_id": revision_id,
                "url": fandom_url(title),
            }
        )
        source_ids[title] = source.id

    universal_century = ContinuityFacade(db_session=db_session).create_or_update(
        payload={"name": "Universal Century", "slug": "universal-century"}
    )

    works = WorkFacade(db_session=db_session)
    work_ids: dict[str, uuid.UUID] = {}
    work_pages: dict[str, str] = {}
    for row in WORKS:
        page = row["page"]
        work = works.create_or_update(
            payload={
                "continuity_id": (
                    universal_century.id if row["universal_century"] else None
                ),
                "end_date": row["end_date"],
                "fandom_page_id": PAGES[page][0],
                "fandom_page_title": page,
                "slug": row["slug"],
                "start_date": row["start_date"],
                "title": page,
                "title_ja": row["title_ja"],
                "work_type": row["work_type"],
            }
        )
        work_ids[work.slug] = work.id
        work_pages[work.slug] = page
    for from_slug, relation_type, to_slug in WORK_RELATIONS:
        works.create_or_update_relation(
            payload={
                "from_work_id": work_ids[from_slug],
                "relation_type": relation_type,
                "source_id": source_ids[work_pages[from_slug]],
                "to_work_id": work_ids[to_slug],
            }
        )
    for old_slug, work_slug in WORK_SLUG_REDIRECTS.items():
        works.create_or_update_slug_redirect(
            payload={"old_slug": old_slug, "work_id": work_ids[work_slug]}
        )

    suits = MobileSuitFacade(db_session=db_session)
    suit_ids: dict[str, uuid.UUID] = {}
    suit_sources: dict[str, uuid.UUID] = {}
    for row in SUITS:
        suit = suits.create_or_update(
            payload={
                "continuity_id": (
                    universal_century.id if row["universal_century"] else None
                ),
                "fandom_page_id": PAGES[row["page"]][0],
                "model_number": row["model_number"],
                "name": row["name"],
                "name_ja": row["name_ja"],
                "slug": row["slug"],
                "unit_type": UnitType.SUIT,
            }
        )
        suit_ids[suit.slug] = suit.id
        suit_sources[suit.slug] = source_ids[row["page"]]
    base_sheet_ids: dict[str, uuid.UUID] = {}
    for row in SPEC_SHEETS:
        sheet = {key: value for key, value in row.items() if key != "suit"}
        spec_sheet = suits.create_or_update_spec_sheet(
            payload={
                **sheet,
                "mobile_suit_id": suit_ids[row["suit"]],
                "source_id": suit_sources[row["suit"]],
            }
        )
        if spec_sheet.configuration is None:
            base_sheet_ids[row["suit"]] = spec_sheet.id
    _seed_parts(db_session, base_sheet_ids=base_sheet_ids)
    for from_slug, relation_type, to_slug in SUIT_RELATIONS:
        suits.create_or_update_relation(
            payload={
                "from_mobile_suit_id": suit_ids[from_slug],
                "relation_type": relation_type,
                "source_id": suit_sources[from_slug],
                "to_mobile_suit_id": suit_ids[to_slug],
            }
        )
    for row in APPEARANCES:
        suits.create_or_update_appearance(
            payload={
                "first_episode": row.get("first_episode"),
                "is_debut": row["is_debut"],
                "last_episode": row.get("last_episode"),
                "mobile_suit_id": suit_ids[row["suit"]],
                "source_id": suit_sources[row["suit"]],
                "work_id": work_ids[row["work"]],
            }
        )
    for old_slug, suit_slug in SUIT_SLUG_REDIRECTS.items():
        suits.create_or_update_slug_redirect(
            payload={"mobile_suit_id": suit_ids[suit_slug], "old_slug": old_slug}
        )

    _seed_people(
        db_session,
        ids=SeededIds(
            sources=source_ids,
            suits=suit_ids,
            suit_sources=suit_sources,
            works=work_ids,
        ),
    )


def run(db_session: Session, *, force: bool) -> None:
    """Check the guards, seed, and commit.

    Raises:
        SeedRefusedError: when a guard refuses the database.
    """
    check_environment()
    if not force:
        check_no_completed_ingest(db_session)
    seed(db_session)
    db_session.commit()


def main(argv: Sequence[str] | None = None) -> int:
    """Seed the configured database; exit 1 when a guard refuses it."""
    init_logging(app_name="seed-dev")
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--force",
        action="store_true",
        help="seed even after a completed ingest run (never outside dev or test)",
    )
    args = parser.parse_args(argv)

    try:
        check_environment()  # before a session exists to connect anywhere
        scoped_session = DBSessionManager().scoped_session
        try:
            run(scoped_session(), force=args.force)
        finally:
            scoped_session.remove()
    except SeedRefusedError as e:
        logger.error("%s", e)  # a refusal, not a crash: no traceback
        return 1

    logger.info(
        "Seeded suits=%d works=%d characters=%d organizations=%d "
        "designers=%d parts=%d sources=%d",
        len(SUITS),
        len(WORKS),
        len(CHARACTERS),
        len(ORGANIZATIONS),
        len(MECHANICAL_DESIGNERS),
        len(ARMAMENTS) + len(EQUIPMENT) + len(MATERIALS) + len(POWERPLANTS),
        len(PAGES),
    )
    return 0


class _RedirectUpsert(Protocol):
    """A facade's ``create_or_update_slug_redirect``."""

    def __call__(self, *, payload: Mapping[str, Any]) -> object:
        """Upsert one old slug."""
        ...


def _seed_people(db_session: Session, *, ids: SeededIds) -> None:
    """Upsert the characters, organizations and designers, and links.

    Appearances come first: a pilot or organization link with a work
    needs both sides' appearances in it.
    """
    characters = CharacterFacade(db_session=db_session)
    character_ids: dict[str, uuid.UUID] = {}
    for row in CHARACTERS:
        character = characters.create_or_update(
            payload={
                "fandom_page_id": PAGES[row["page"]][0],
                "fandom_page_title": row["page"],
                "name": row["name"],
                "name_ja": row["name_ja"],
                "slug": row["slug"],
            }
        )
        character_ids[character.slug] = character.id
        for work_slug in row["works"]:
            characters.create_or_update_appearance(
                payload={
                    "character_id": character.id,
                    "source_id": ids.sources[row["page"]],
                    "work_id": ids.works[work_slug],
                }
            )
    _seed_redirects(
        characters.create_or_update_slug_redirect,
        CHARACTER_SLUG_REDIRECTS,
        target_ids=character_ids,
        target_column="character_id",
    )

    organizations = OrganizationFacade(db_session=db_session)
    organization_ids: dict[str, uuid.UUID] = {}
    for row in ORGANIZATIONS:
        organization = organizations.create_or_update(
            payload={
                "fandom_page_id": PAGES[row["page"]][0],
                "fandom_page_title": row["page"],
                "name": row["page"],
                "parent_organization_id": None,
                "slug": row["slug"],
            }
        )
        organization_ids[organization.slug] = organization.id
        for work_slug in row["works"]:
            organizations.create_or_update_appearance(
                payload={
                    "organization_id": organization.id,
                    "source_id": ids.sources[row["page"]],
                    "work_id": ids.works[work_slug],
                }
            )
    _seed_redirects(
        organizations.create_or_update_slug_redirect,
        ORGANIZATION_SLUG_REDIRECTS,
        target_ids=organization_ids,
        target_column="organization_id",
    )

    designers = MechanicalDesignerFacade(db_session=db_session)
    designer_ids: dict[str, uuid.UUID] = {}
    for row in MECHANICAL_DESIGNERS:
        page = row["page"]
        designer = designers.create_or_update(
            payload={
                "fandom_page_id": None if page is None else PAGES[page][0],
                "fandom_page_title": page,
                "name": row["name"],
                "name_ja": row["name_ja"],
                "slug": row["slug"],
            }
        )
        designer_ids[designer.slug] = designer.id
    _seed_redirects(
        designers.create_or_update_slug_redirect,
        MECHANICAL_DESIGNER_SLUG_REDIRECTS,
        target_ids=designer_ids,
        target_column="mechanical_designer_id",
    )

    pilots = MobileSuitPilotFacade(db_session=db_session)
    for pilot in PILOTS:
        pilots.create_or_update(
            payload={
                "character_id": character_ids[pilot.character],
                "mobile_suit_id": ids.suits[pilot.suit],
                "source_id": ids.suit_sources[pilot.suit],
                "work_id": _optional_id(ids.works, pilot.work),
            }
        )
    suit_organizations = MobileSuitOrganizationFacade(db_session=db_session)
    for link in SUIT_ORGANIZATIONS:
        suit_organizations.create_or_update(
            payload={
                "mobile_suit_id": ids.suits[link.suit],
                "organization_id": organization_ids[link.organization],
                "role": link.role,
                "source_id": ids.suit_sources[link.suit],
                "work_id": _optional_id(ids.works, link.work),
            }
        )
    suit_designers = MobileSuitDesignerFacade(db_session=db_session)
    for suit_slug, designer_slug in SUIT_DESIGNERS:
        suit_designers.create_or_update(
            payload={
                "mechanical_designer_id": designer_ids[designer_slug],
                "mobile_suit_id": ids.suits[suit_slug],
                "source_id": ids.suit_sources[suit_slug],
            }
        )


class _Upserted(Protocol):
    """An upserted row's entity, read only for its ``id``."""

    @property
    def id(self) -> uuid.UUID:
        """The row's primary key."""
        ...


class _PartUpsert(Protocol):
    """A part facade's ``create_or_update``."""

    def __call__(self, *, payload: Mapping[str, Any]) -> _Upserted:
        """Upsert one part."""
        ...


def _seed_parts(
    db_session: Session, *, base_sheet_ids: Mapping[str, uuid.UUID]
) -> None:
    """Upsert the parts, then list them on each suit's base sheet.

    The infobox lists parts once, so the named configurations inherit
    them (``inherited_parts``).
    """
    part_upserts: tuple[tuple[SpecSheetPartKind, _PartUpsert, list[PartRow]], ...] = (
        (
            "armaments",
            ArmamentFacade(db_session=db_session).create_or_update,
            ARMAMENTS,
        ),
        (
            "equipment",
            EquipmentFacade(db_session=db_session).create_or_update,
            EQUIPMENT,
        ),
        (
            "materials",
            MaterialFacade(db_session=db_session).create_or_update,
            MATERIALS,
        ),
        (
            "powerplants",
            PowerplantFacade(db_session=db_session).create_or_update,
            POWERPLANTS,
        ),
    )
    part_ids: dict[SpecSheetPartKind, dict[str, uuid.UUID]] = {}
    for kind, upsert, rows in part_upserts:
        part_ids[kind] = {
            row.slug: upsert(
                payload={
                    "fandom_page_id": row.page_id,
                    "fandom_page_title": None if row.page_id is None else row.name,
                    "name": row.name,
                    "slug": row.slug,
                }
            ).id
            for row in rows
        }

    armaments = SpecSheetArmamentFacade(db_session=db_session)
    for listing in SHEET_ARMAMENTS:
        armaments.create_or_update(
            payload={
                "armament_id": part_ids["armaments"][listing.armament],
                "mount": listing.mount,
                "note": listing.note,
                "quantity_max": listing.quantity_max,
                "quantity_min": listing.quantity_min,
                "spec_sheet_id": base_sheet_ids[listing.suit],
            }
        )
    equipment = SpecSheetEquipmentFacade(db_session=db_session)
    for listing in SHEET_EQUIPMENT:
        equipment.create_or_update(
            payload={
                "equipment_id": part_ids["equipment"][listing.equipment],
                "fit": listing.fit,
                "note": listing.note,
                "spec_sheet_id": base_sheet_ids[listing.suit],
            }
        )
    materials = SpecSheetMaterialFacade(db_session=db_session)
    for listing in SHEET_MATERIALS:
        materials.create_or_update(
            payload={
                "material_id": part_ids["materials"][listing.material],
                "material_use": listing.material_use,
                "note": listing.note,
                "spec_sheet_id": base_sheet_ids[listing.suit],
            }
        )
    powerplants = SpecSheetPowerplantFacade(db_session=db_session)
    for listing in SHEET_POWERPLANTS:
        powerplants.create_or_update(
            payload={
                "note": listing.note,
                "powerplant_id": part_ids["powerplants"][listing.powerplant],
                "quantity_max": listing.quantity_max,
                "quantity_min": listing.quantity_min,
                "spec_sheet_id": base_sheet_ids[listing.suit],
            }
        )


def _seed_redirects(
    upsert: _RedirectUpsert,
    redirects: Mapping[str, str],
    *,
    target_ids: Mapping[str, uuid.UUID],
    target_column: str,
) -> None:
    """Upsert each old slug, pointing it at its current slug's row."""
    for old_slug, current_slug in redirects.items():
        upsert(payload={"old_slug": old_slug, target_column: target_ids[current_slug]})


def _optional_id(ids: Mapping[str, uuid.UUID], slug: str | None) -> uuid.UUID | None:
    """Look up a slug that may be null: a link with no recorded work."""
    return None if slug is None else ids[slug]


if __name__ == "__main__":
    sys.exit(main())
