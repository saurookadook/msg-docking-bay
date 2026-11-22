import uuid
from datetime import date, datetime
from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from _factories.armament.db import ArmamentDBFactory
from _factories.character.db import CharacterDBFactory
from _factories.character_appearance.db import CharacterAppearanceDBFactory
from _factories.continuity.db import ContinuityDBFactory
from _factories.equipment.db import EquipmentDBFactory
from _factories.material.db import MaterialDBFactory
from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_appearance.db import MobileSuitAppearanceDBFactory
from _factories.mobile_suit_designer.db import MobileSuitDesignerDBFactory
from _factories.mobile_suit_organization.db import MobileSuitOrganizationDBFactory
from _factories.mobile_suit_pilot.db import MobileSuitPilotDBFactory
from _factories.mobile_suit_relation.db import MobileSuitRelationDBFactory
from _factories.mobile_suit_slug_redirect.db import MobileSuitSlugRedirectDBFactory
from _factories.organization.db import OrganizationDBFactory
from _factories.organization_appearance.db import OrganizationAppearanceDBFactory
from _factories.powerplant.db import PowerplantDBFactory
from _factories.source.db import SourceDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.spec_sheet_armament.db import SpecSheetArmamentDBFactory
from _factories.spec_sheet_equipment.db import SpecSheetEquipmentDBFactory
from _factories.spec_sheet_material.db import SpecSheetMaterialDBFactory
from _factories.spec_sheet_powerplant.db import SpecSheetPowerplantDBFactory
from _factories.work.db import WorkDBFactory
from _factories.work_slug_redirect.db import WorkSlugRedirectDBFactory
from constants.catalog import (
    MobileSuitOrganizationRole,
    MobileSuitRelationType,
    SourceKind,
    UnitType,
)
from models._tests.query_count import CountStatements
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit.entity import MobileSuitCardEntity
from models.mobile_suit.facade import MobileSuitFacade
from models.spec_sheet.entity import SPEC_SHEET_PART_KINDS
from models.work.facade import WorkFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf002")
ORIGIN_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf003")
GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf004")
ORIGIN_GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf005")
ZAKU_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf006")
ACT_ZAKU_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf007")
TURN_A_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf008")
WIKI_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf009")
MAHQ_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bf00a")


@pytest.fixture
def suits(test_db_session: Session) -> None:
    """Five suits; three in the 1979 series, one new in The Origin."""
    ContinuityDBFactory(id=UC_ID, name="Universal Century", slug="universal-century")
    WorkDBFactory(
        id=MSG_ID,
        continuity_id=UC_ID,
        slug="mobile-suit-gundam",
        start_date=date(1979, 4, 7),
        title="Mobile Suit Gundam",
    )
    WorkDBFactory(
        id=ORIGIN_ID,
        continuity_id=UC_ID,
        slug="mobile-suit-gundam-the-origin",
        start_date=date(2015, 2, 28),
        title="Mobile Suit Gundam: The Origin",
    )
    MobileSuitDBFactory(
        id=GUNDAM_ID,
        continuity_id=UC_ID,
        model_number="RX-78-2",
        name="Gundam",
        slug="rx-78-2-gundam",
    )
    MobileSuitDBFactory(
        id=ORIGIN_GUNDAM_ID,
        continuity_id=UC_ID,
        model_number="RX-78-02",
        name="Gundam (The Origin)",
        slug="rx-78-02-gundam",
    )
    MobileSuitDBFactory(
        id=ZAKU_ID,
        continuity_id=UC_ID,
        model_number="MS-06F",
        name="Zaku II",
        slug="zaku-ii",
    )
    MobileSuitDBFactory(
        id=ACT_ZAKU_ID,
        continuity_id=UC_ID,
        model_number="MS-11",
        name="Act Zaku",
        slug="act-zaku",
    )
    MobileSuitDBFactory(
        id=TURN_A_ID,
        model_number="SYSTEM-∀99",
        name="∀ Gundam",
        slug="turn-a-gundam",
        unit_type=UnitType.DOLL,
    )
    SourceDBFactory(id=WIKI_ID, url="https://gundam.fandom.com/?curid=2034")
    for suit_id, is_debut in ((GUNDAM_ID, True), (ZAKU_ID, True), (ACT_ZAKU_ID, False)):
        MobileSuitAppearanceDBFactory(
            mobile_suit_id=suit_id, is_debut=is_debut, source_id=WIKI_ID, work_id=MSG_ID
        )
    MobileSuitAppearanceDBFactory(
        mobile_suit_id=ORIGIN_GUNDAM_ID,
        is_debut=True,
        source_id=WIKI_ID,
        work_id=ORIGIN_ID,
    )
    MobileSuitAppearanceDBFactory(
        mobile_suit_id=GUNDAM_ID,
        first_episode=1,
        last_episode=13,
        source_id=WIKI_ID,
        work_id=ORIGIN_ID,
    )
    test_db_session.commit()


def list_parts(test_db_session: Session, sheet_id: uuid.UUID, *, count: int) -> None:
    """List ``count`` new parts of every kind on one sheet."""
    parts = [
        (
            ArmamentDBFactory(),
            EquipmentDBFactory(),
            MaterialDBFactory(),
            PowerplantDBFactory(),
        )
        for _ in range(count)
    ]
    test_db_session.flush()
    for armament, equipment, material, powerplant in parts:
        SpecSheetArmamentDBFactory(armament_id=armament.id, spec_sheet_id=sheet_id)
        SpecSheetEquipmentDBFactory(equipment_id=equipment.id, spec_sheet_id=sheet_id)
        SpecSheetMaterialDBFactory(material_id=material.id, spec_sheet_id=sheet_id)
        SpecSheetPowerplantDBFactory(
            powerplant_id=powerplant.id, spec_sheet_id=sheet_id
        )


def slugs(items: list[MobileSuitCardEntity]) -> list[str]:
    return [suit.slug for suit in items]


def page(test_db_session: Session, **filters: Any) -> list[str]:
    facade = MobileSuitFacade(db_session=test_db_session)
    return slugs(facade.get_page(**filters, limit=50, offset=0).items)


@pytest.mark.usefixtures("suits")
class TestMobileSuitFacadeGetPage:
    def test_get_page(self, test_db_session: Session, mock_utcnow: datetime) -> None:
        result = MobileSuitFacade(db_session=test_db_session).get_page(
            limit=2, offset=2
        )

        assert slugs(result.items) == ["rx-78-2-gundam", "rx-78-02-gundam"]
        assert result.total == 5
        assert result.items[0].model_dump() == {
            "continuity": {"name": "Universal Century", "slug": "universal-century"},
            "created_at": mock_utcnow,
            "model_number": "RX-78-2",
            "name": "Gundam",
            "name_ja": None,
            "slug": "rx-78-2-gundam",
            "unit_type": UnitType.SUIT,
            "updated_at": mock_utcnow,
        }

    def test_get_page_by_name(self, test_db_session: Session) -> None:
        """In the database's collation, which skips the ``∀``."""
        assert page(test_db_session) == [
            "act-zaku",
            "turn-a-gundam",
            "rx-78-2-gundam",
            "rx-78-02-gundam",
            "zaku-ii",
        ]

    def test_get_page_past_the_end(self, test_db_session: Session) -> None:
        result = MobileSuitFacade(db_session=test_db_session).get_page(
            limit=50, offset=50
        )

        assert (result.items, result.total) == ([], 5)

    @pytest.mark.parametrize(
        ("filters", "expected"),
        [
            ({"unit_type": UnitType.DOLL}, ["turn-a-gundam"]),
            (
                {"continuity_slug": "universal-century"},
                ["act-zaku", "rx-78-2-gundam", "rx-78-02-gundam", "zaku-ii"],
            ),
            (
                {"work_slug": "mobile-suit-gundam"},
                ["act-zaku", "rx-78-2-gundam", "zaku-ii"],
            ),
            (
                {"work_slug": "mobile-suit-gundam-the-origin", "q": "rx78"},
                ["rx-78-2-gundam", "rx-78-02-gundam"],
            ),
            ({"continuity_slug": "cosmic-era"}, []),
            ({"work_slug": "gundam-0079"}, []),
        ],
    )
    def test_get_page_filters(
        self, test_db_session: Session, filters: dict[str, Any], expected: list[str]
    ) -> None:
        assert page(test_db_session, **filters) == expected

    @pytest.mark.parametrize(
        ("q", "expected"),
        [
            ("rx782", ["rx-78-2-gundam"]),
            ("RX-78-2", ["rx-78-2-gundam"]),
            ("turn a", ["turn-a-gundam"]),
            ("ms06", ["zaku-ii"]),
            ("rx%02", []),
        ],
    )
    def test_get_page_q_matches_normalized_slug_and_model_number(
        self, test_db_session: Session, q: str, expected: list[str]
    ) -> None:
        """``%`` and ``_`` are dropped, never read as wildcards (D8)."""
        assert page(test_db_session, q=q) == expected

    def test_get_page_q_ranks_prefix_matches_first(
        self, test_db_session: Session
    ) -> None:
        """A prefix match ranks first: Zaku II before Act Zaku (D8)."""
        assert page(test_db_session, q="zaku") == ["zaku-ii", "act-zaku"]

    @pytest.mark.parametrize("q", [" -- ", "%_", "∀"])
    def test_get_page_blank_q_is_no_filter(
        self, test_db_session: Session, q: str
    ) -> None:
        assert len(page(test_db_session, q=q)) == 5


@pytest.mark.usefixtures("suits")
class TestMobileSuitFacadeGetPageByWorkSlug:
    def test_get_page_by_work_slug(self, test_db_session: Session) -> None:
        """Suits that debut in the work come first, then by name."""
        result = MobileSuitFacade(db_session=test_db_session).get_page_by_work_slug(
            "mobile-suit-gundam-the-origin", limit=50, offset=0
        )

        assert [(s.slug, s.is_debut, s.first_episode) for s in result.items] == [
            ("rx-78-02-gundam", True, None),
            ("rx-78-2-gundam", False, 1),
        ]
        assert result.items[1].last_episode == 13
        assert result.total == 2

    def test_get_page_by_work_slug_debuts_first(self, test_db_session: Session) -> None:
        result = MobileSuitFacade(db_session=test_db_session).get_page_by_work_slug(
            "mobile-suit-gundam", limit=2, offset=0
        )

        assert slugs(list(result.items)) == ["rx-78-2-gundam", "zaku-ii"]
        assert result.total == 3

    def test_get_page_by_work_slug_old_slug(self, test_db_session: Session) -> None:
        WorkSlugRedirectDBFactory(old_slug="gundam-0079", work_id=MSG_ID)
        test_db_session.commit()

        result = MobileSuitFacade(db_session=test_db_session).get_page_by_work_slug(
            "gundam-0079", limit=50, offset=0
        )

        assert result.total == 3

    def test_get_page_by_work_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(WorkFacade.NotFoundError):
            MobileSuitFacade(db_session=test_db_session).get_page_by_work_slug(
                "turn-a-gundam-series", limit=50, offset=0
            )


@pytest.mark.usefixtures("suits")
class TestMobileSuitFacadeGetOneBySlug:
    def test_get_one_by_slug(self, test_db_session: Session) -> None:
        suit = MobileSuitFacade(db_session=test_db_session).get_one_by_slug(
            "rx-78-2-gundam"
        )

        assert suit.slug == "rx-78-2-gundam"
        assert [(a.work.slug, a.is_debut) for a in suit.appearances] == [
            ("mobile-suit-gundam", True),
            ("mobile-suit-gundam-the-origin", False),
        ]
        assert suit.appearances[0].source.url == "https://gundam.fandom.com/?curid=2034"
        assert suit.relations == []
        assert suit.spec_sheets == []

    def test_get_one_by_slug_old_slug(self, test_db_session: Session) -> None:
        MobileSuitSlugRedirectDBFactory(
            mobile_suit_id=GUNDAM_ID, old_slug="gundam-rx-78-2"
        )
        test_db_session.commit()

        suit = MobileSuitFacade(db_session=test_db_session).get_one_by_slug(
            "gundam-rx-78-2"
        )

        assert suit.slug == "rx-78-2-gundam"

    def test_get_one_by_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(MobileSuitFacade.NotFoundError, match="slug='gp01'"):
            MobileSuitFacade(db_session=test_db_session).get_one_by_slug("gp01")

    def test_get_one_by_slug_relations_from_each_side(
        self, test_db_session: Session
    ) -> None:
        """The Origin's Gundam is an alternate version of RX-78-2."""
        MobileSuitRelationDBFactory(
            from_mobile_suit_id=ORIGIN_GUNDAM_ID,
            relation_type=MobileSuitRelationType.ALTERNATE_VERSION_OF,
            source_id=WIKI_ID,
            to_mobile_suit_id=GUNDAM_ID,
        )
        MobileSuitRelationDBFactory(
            from_mobile_suit_id=GUNDAM_ID,
            relation_type=MobileSuitRelationType.DEVELOPED_FROM,
            source_id=WIKI_ID,
            to_mobile_suit_id=ZAKU_ID,
        )
        test_db_session.commit()
        facade = MobileSuitFacade(db_session=test_db_session)

        gundam = facade.get_one_by_slug("rx-78-2-gundam")
        origin = facade.get_one_by_slug("rx-78-02-gundam")

        assert [
            (r.relation_type, r.direction, r.mobile_suit.slug) for r in gundam.relations
        ] == [
            (MobileSuitRelationType.DEVELOPED_FROM, "outgoing", "zaku-ii"),
            (
                MobileSuitRelationType.ALTERNATE_VERSION_OF,
                "incoming",
                "rx-78-02-gundam",
            ),
        ]
        assert [(r.direction, r.mobile_suit.slug) for r in origin.relations] == [
            ("outgoing", "rx-78-2-gundam")
        ]

    def test_get_one_by_slug_fills_named_sheets_from_the_same_source(
        self, test_db_session: Session
    ) -> None:
        SourceDBFactory(id=MAHQ_ID, kind=SourceKind.WIKIDATA_ITEM)
        SpecSheetDBFactory(
            mobile_suit_id=GUNDAM_ID,
            source_id=WIKI_ID,
            head_height_m=18.0,
            gross_weight_kg=60000.0,
        )
        SpecSheetDBFactory(
            configuration="G-Armor",
            mobile_suit_id=GUNDAM_ID,
            source_id=WIKI_ID,
            gross_weight_kg=80000.0,
        )
        SpecSheetDBFactory(
            configuration="Full Armor",
            mobile_suit_id=GUNDAM_ID,
            source_id=MAHQ_ID,
            gross_weight_kg=75000.0,
        )
        test_db_session.commit()

        sheets = (
            MobileSuitFacade(db_session=test_db_session)
            .get_one_by_slug("rx-78-2-gundam")
            .spec_sheets
        )

        assert [
            (s.configuration, s.head_height_m, s.gross_weight_kg, s.inherited_fields)
            for s in sheets
        ] == [
            (None, 18.0, 60000.0, []),
            ("Full Armor", None, 75000.0, []),
            ("G-Armor", 18.0, 80000.0, ["head_height_m"]),
        ]
        assert sheets[1].source.kind is SourceKind.WIKIDATA_ITEM

    def test_get_one_by_slug_sends_a_fixed_number_of_statements(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """A row of each kind costs what five do (PYTEST-24).

        Eleven: seven for the suit, its lists and its sheets, then one
        for each of the four part kinds, whatever the sheet count.
        """
        for suit_id, count in ((ZAKU_ID, 5), (ACT_ZAKU_ID, 1)):
            for _ in range(count):
                character = CharacterDBFactory()
                designer = MechanicalDesignerDBFactory()
                organization = OrganizationDBFactory()
                test_db_session.flush()
                MobileSuitPilotDBFactory(
                    character_id=character.id, mobile_suit_id=suit_id, source_id=WIKI_ID
                )
                MobileSuitOrganizationDBFactory(
                    mobile_suit_id=suit_id,
                    organization_id=organization.id,
                    source_id=WIKI_ID,
                )
                MobileSuitDesignerDBFactory(
                    mechanical_designer_id=designer.id,
                    mobile_suit_id=suit_id,
                    source_id=WIKI_ID,
                )
        zaku_sheet = SpecSheetDBFactory(mobile_suit_id=ZAKU_ID, source_id=WIKI_ID)
        list_parts(test_db_session, zaku_sheet.id, count=5)
        for index in range(1, 5):
            SpecSheetDBFactory(
                configuration=f"Config {index}",
                mobile_suit_id=ZAKU_ID,
                source_id=WIKI_ID,
            )
        for _ in range(5):
            other = MobileSuitDBFactory(continuity_id=UC_ID)
            work = WorkDBFactory(continuity_id=UC_ID)
            source = SourceDBFactory()
            MobileSuitRelationDBFactory(
                from_mobile_suit_id=ZAKU_ID,
                relation_type=MobileSuitRelationType.VARIANT_OF,
                source_id=source.id,
                to_mobile_suit_id=other.id,
            )
            MobileSuitAppearanceDBFactory(
                mobile_suit_id=ZAKU_ID, source_id=source.id, work_id=work.id
            )
        MobileSuitRelationDBFactory(
            from_mobile_suit_id=ACT_ZAKU_ID,
            relation_type=MobileSuitRelationType.UPGRADE_OF,
            source_id=WIKI_ID,
            to_mobile_suit_id=ZAKU_ID,
        )
        act_zaku_sheet = SpecSheetDBFactory(
            mobile_suit_id=ACT_ZAKU_ID, source_id=WIKI_ID
        )
        list_parts(test_db_session, act_zaku_sheet.id, count=1)
        test_db_session.commit()
        facade = MobileSuitFacade(db_session=test_db_session)

        with count_statements() as few:
            act_zaku = facade.get_one_by_slug("act-zaku")
        with count_statements() as many:
            zaku = facade.get_one_by_slug("zaku-ii")

        assert (len(act_zaku.relations), len(zaku.relations)) == (1, 6)
        assert (len(act_zaku.pilots), len(zaku.pilots)) == (1, 5)
        assert (len(act_zaku.organizations), len(zaku.organizations)) == (1, 5)
        assert (len(act_zaku.designers), len(zaku.designers)) == (1, 5)
        for kind in SPEC_SHEET_PART_KINDS:
            assert len(getattr(act_zaku.spec_sheets[0], kind)) == 1
            assert {len(getattr(sheet, kind)) for sheet in zaku.spec_sheets} == {5}
        assert few.value == many.value == 11

    def test_get_one_by_slug_without_sheets_skips_the_part_queries(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """No sheets, no part queries: the suit and its six lists."""
        facade = MobileSuitFacade(db_session=test_db_session)

        with count_statements() as count:
            turn_a = facade.get_one_by_slug("turn-a-gundam")

        assert (turn_a.spec_sheets, count.value) == ([], 7)

    def test_get_one_by_slug_inherits_empty_part_lists(
        self, test_db_session: Session
    ) -> None:
        """A named sheet takes each empty kind from its base sheet.

        Its own list wins where it has one, a sheet from another source
        inherits nothing, and a base sheet never does.
        """
        SourceDBFactory(id=MAHQ_ID, kind=SourceKind.WIKIDATA_ITEM)
        sheet_ids: dict[str | None, uuid.UUID] = {}
        for configuration, source_id in (
            (None, WIKI_ID),
            ("G-Armor", WIKI_ID),
            ("Magnet Coating", WIKI_ID),
            ("Full Armor", MAHQ_ID),
        ):
            sheet_ids[configuration] = SpecSheetDBFactory(
                configuration=configuration,
                mobile_suit_id=GUNDAM_ID,
                source_id=source_id,
            ).id
        rifle = ArmamentDBFactory(name="Beam Rifle")
        cannon = ArmamentDBFactory(name="Beam Cannon")
        core_block = EquipmentDBFactory(name="Core Block System")
        test_db_session.flush()
        SpecSheetArmamentDBFactory(armament_id=rifle.id, spec_sheet_id=sheet_ids[None])
        SpecSheetArmamentDBFactory(
            armament_id=cannon.id, spec_sheet_id=sheet_ids["G-Armor"]
        )
        SpecSheetEquipmentDBFactory(
            equipment_id=core_block.id, spec_sheet_id=sheet_ids[None]
        )
        test_db_session.commit()

        sheets = (
            MobileSuitFacade(db_session=test_db_session)
            .get_one_by_slug("rx-78-2-gundam")
            .spec_sheets
        )

        assert [
            (
                sheet.configuration,
                [listing.armament.name for listing in sheet.armaments],
                [listing.equipment.name for listing in sheet.equipment],
                sheet.inherited_parts,
            )
            for sheet in sheets
        ] == [
            (None, ["Beam Rifle"], ["Core Block System"], []),
            ("Full Armor", [], [], []),
            ("G-Armor", ["Beam Cannon"], ["Core Block System"], ["equipment"]),
            (
                "Magnet Coating",
                ["Beam Rifle"],
                ["Core Block System"],
                ["armaments", "equipment"],
            ),
        ]
        assert all(sheet.inherited_fields == [] for sheet in sheets)


@pytest.mark.usefixtures("suits")
class TestMobileSuitFacadeWrites:
    def test_create_or_update(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        payload = {
            "model_number": "RX-78-2",
            "name": "Gundam",
            "slug": "rx-78-2-gundam",
            "unit_type": UnitType.SUIT,
        }
        facade = MobileSuitFacade(db_session=test_db_session)

        unchanged = facade.create_or_update(payload=payload)
        changed = facade.create_or_update(payload={**payload, "fandom_page_id": 2034})

        assert unchanged.id == changed.id == GUNDAM_ID
        assert unchanged.updated_at == mock_utcnow
        assert changed.updated_at != mock_utcnow

    def test_create_or_update_spec_sheet_upserts_the_base_sheet(
        self, test_db_session: Session
    ) -> None:
        """A null configuration still finds the existing base sheet."""
        facade = MobileSuitFacade(db_session=test_db_session)
        payload = {
            "configuration": None,
            "head_height_m": 18.0,
            "mobile_suit_id": GUNDAM_ID,
            "source_id": WIKI_ID,
        }

        first = facade.create_or_update_spec_sheet(payload=payload)
        second = facade.create_or_update_spec_sheet(
            payload={**payload, "head_height_m": 18.5}
        )

        assert second.id == first.id
        assert second.head_height_m == 18.5

    def test_create_or_update_relation(self, test_db_session: Session) -> None:
        relation = MobileSuitFacade(
            db_session=test_db_session
        ).create_or_update_relation(
            payload={
                "from_mobile_suit_id": ORIGIN_GUNDAM_ID,
                "relation_type": MobileSuitRelationType.ALTERNATE_VERSION_OF,
                "source_id": WIKI_ID,
                "to_mobile_suit_id": GUNDAM_ID,
            }
        )

        assert relation.to_mobile_suit_id == GUNDAM_ID

    def test_create_or_update_appearance(self, test_db_session: Session) -> None:
        appearance = MobileSuitFacade(
            db_session=test_db_session
        ).create_or_update_appearance(
            payload={
                "first_episode": 1,
                "is_debut": True,
                "last_episode": 43,
                "mobile_suit_id": GUNDAM_ID,
                "source_id": WIKI_ID,
                "work_id": MSG_ID,
            }
        )

        assert (appearance.first_episode, appearance.last_episode) == (1, 43)

    def test_create_or_update_slug_redirect(self, test_db_session: Session) -> None:
        redirect = MobileSuitFacade(
            db_session=test_db_session
        ).create_or_update_slug_redirect(
            payload={"mobile_suit_id": GUNDAM_ID, "old_slug": "gundam-rx-78-2"}
        )

        assert redirect.mobile_suit_id == GUNDAM_ID


class TestMobileSuitCardEntity:
    def test_fails_on_a_row_whose_continuity_was_not_loaded(
        self, test_db_session: Session
    ) -> None:
        MobileSuitDBFactory()
        test_db_session.commit()
        test_db_session.expunge_all()
        row = test_db_session.scalars(select(MobileSuitDB)).one()

        with pytest.raises(ValidationError, match="get_attribute_error"):
            MobileSuitCardEntity.model_validate(row)


@pytest.mark.usefixtures("suits")
class TestMobileSuitFacadeCredits:
    def test_get_one_by_slug_lists_its_credits(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """Refs only (Q5); a credit with no work comes last (Q2)."""
        amuro = CharacterDBFactory(name="Amuro Ray", slug="amuro-ray")
        sayla = CharacterDBFactory(name="Sayla Mass", slug="sayla-mass")
        kai = CharacterDBFactory(name="Kai Shiden", slug="kai-shiden")
        federation = OrganizationDBFactory(
            name="Earth Federation", slug="earth-federation"
        )
        anaheim = OrganizationDBFactory(
            name="Anaheim Electronics", slug="anaheim-electronics"
        )
        okawara = MechanicalDesignerDBFactory(
            name="Kunio Okawara", slug="kunio-okawara"
        )
        katoki = MechanicalDesignerDBFactory(name="Hajime Katoki", slug="hajime-katoki")
        test_db_session.flush()
        for character in (amuro, sayla):
            CharacterAppearanceDBFactory(
                character_id=character.id, source_id=WIKI_ID, work_id=MSG_ID
            )
        CharacterAppearanceDBFactory(
            character_id=amuro.id, source_id=WIKI_ID, work_id=ORIGIN_ID
        )
        for organization_id, work_id in (
            (federation.id, MSG_ID),
            (federation.id, ORIGIN_ID),
        ):
            OrganizationAppearanceDBFactory(
                organization_id=organization_id, source_id=WIKI_ID, work_id=work_id
            )
        test_db_session.flush()
        for character_id, work_id in (
            (kai.id, None),
            (amuro.id, ORIGIN_ID),
            (sayla.id, MSG_ID),
            (amuro.id, MSG_ID),
        ):
            MobileSuitPilotDBFactory(
                character_id=character_id,
                mobile_suit_id=GUNDAM_ID,
                source_id=WIKI_ID,
                work_id=work_id,
            )
        for organization_id, role, work_id in (
            (anaheim.id, MobileSuitOrganizationRole.OPERATOR, None),
            (federation.id, MobileSuitOrganizationRole.DEVELOPER, MSG_ID),
            (federation.id, MobileSuitOrganizationRole.OPERATOR, ORIGIN_ID),
            (federation.id, MobileSuitOrganizationRole.OPERATOR, MSG_ID),
        ):
            MobileSuitOrganizationDBFactory(
                mobile_suit_id=GUNDAM_ID,
                organization_id=organization_id,
                role=role,
                source_id=WIKI_ID,
                work_id=work_id,
            )
        for designer in (okawara, katoki):
            MobileSuitDesignerDBFactory(
                mechanical_designer_id=designer.id,
                mobile_suit_id=GUNDAM_ID,
                source_id=WIKI_ID,
            )
        test_db_session.commit()

        gundam = MobileSuitFacade(db_session=test_db_session).get_one_by_slug(
            "rx-78-2-gundam"
        )

        assert [
            (p.character.slug, p.work.slug if p.work else None) for p in gundam.pilots
        ] == [
            ("amuro-ray", "mobile-suit-gundam"),
            ("sayla-mass", "mobile-suit-gundam"),
            ("amuro-ray", "mobile-suit-gundam-the-origin"),
            ("kai-shiden", None),
        ]
        assert gundam.pilots[0].character.model_dump() == {
            "name": "Amuro Ray",
            "slug": "amuro-ray",
        }
        assert gundam.pilots[0].source.url == "https://gundam.fandom.com/?curid=2034"
        assert gundam.pilots[0].created_at == mock_utcnow
        assert [
            (o.role, o.work.slug if o.work else None, o.organization.slug)
            for o in gundam.organizations
        ] == [
            (
                MobileSuitOrganizationRole.OPERATOR,
                "mobile-suit-gundam",
                "earth-federation",
            ),
            (
                MobileSuitOrganizationRole.OPERATOR,
                "mobile-suit-gundam-the-origin",
                "earth-federation",
            ),
            (MobileSuitOrganizationRole.OPERATOR, None, "anaheim-electronics"),
            (
                MobileSuitOrganizationRole.DEVELOPER,
                "mobile-suit-gundam",
                "earth-federation",
            ),
        ]
        assert [d.mechanical_designer.slug for d in gundam.designers] == [
            "hajime-katoki",
            "kunio-okawara",
        ]
        assert gundam.designers[0].source.url == (
            "https://gundam.fandom.com/?curid=2034"
        )

    def test_get_one_by_slug_with_no_credits(self, test_db_session: Session) -> None:
        zaku = MobileSuitFacade(db_session=test_db_session).get_one_by_slug("zaku-ii")

        assert (zaku.pilots, zaku.organizations, zaku.designers) == ([], [], [])
