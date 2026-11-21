import uuid
from datetime import date, datetime
from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_appearance.db import MobileSuitAppearanceDBFactory
from _factories.mobile_suit_relation.db import MobileSuitRelationDBFactory
from _factories.mobile_suit_slug_redirect.db import MobileSuitSlugRedirectDBFactory
from _factories.source.db import SourceDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.work.db import WorkDBFactory
from _factories.work_slug_redirect.db import WorkSlugRedirectDBFactory
from constants.catalog import MobileSuitRelationType, SourceKind, UnitType
from models._tests.query_count import CountStatements
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit.entity import MobileSuitCardEntity
from models.mobile_suit.facade import MobileSuitFacade
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
        """A row of each kind costs what five do (PYTEST-24)."""
        for index in range(5):
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
            SpecSheetDBFactory(
                configuration=None if index == 0 else f"Config {index}",
                mobile_suit_id=ZAKU_ID,
                source_id=WIKI_ID,
            )
        MobileSuitRelationDBFactory(
            from_mobile_suit_id=ACT_ZAKU_ID,
            relation_type=MobileSuitRelationType.UPGRADE_OF,
            source_id=WIKI_ID,
            to_mobile_suit_id=ZAKU_ID,
        )
        SpecSheetDBFactory(mobile_suit_id=ACT_ZAKU_ID, source_id=WIKI_ID)
        test_db_session.commit()
        facade = MobileSuitFacade(db_session=test_db_session)

        with count_statements() as few:
            act_zaku = facade.get_one_by_slug("act-zaku")
        with count_statements() as many:
            zaku = facade.get_one_by_slug("zaku-ii")

        assert (len(act_zaku.relations), len(zaku.relations)) == (1, 6)
        assert few.value == many.value == 4


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
