from typing import Final

import pytest
from sqlalchemy.orm import Session

from _factories.character.db import CharacterDBFactory
from _factories.continuity.db import ContinuityDBFactory
from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.organization.db import OrganizationDBFactory
from _factories.work.db import WorkDBFactory
from models._tests.query_count import CountStatements
from models.search.entity import CatalogSearch
from models.search.facade import CatalogSearchFacade

NO_MATCHES: Final[dict[str, list[str]]] = {
    "characters": [],
    "mechanical_designers": [],
    "mobile_suits": [],
    "organizations": [],
    "works": [],
}


@pytest.fixture
def catalog(test_db_session: Session) -> None:
    """A few rows of every kind, with Zeon in two organizations."""
    MobileSuitDBFactory(model_number="RX-78-2", name="Gundam", slug="rx-78-2-gundam")
    MobileSuitDBFactory(model_number="MS-06F", name="Zaku II", slug="zaku-ii")
    MobileSuitDBFactory(model_number="MS-11", name="Act Zaku", slug="act-zaku")
    CharacterDBFactory(name="Amuro Ray", slug="amuro-ray")
    CharacterDBFactory(name="Char Aznable", slug="char-aznable")
    OrganizationDBFactory(name="Earth Federation", slug="earth-federation")
    OrganizationDBFactory(name="Principality of Zeon", slug="principality-of-zeon")
    OrganizationDBFactory(name="Zeonic", slug="zeonic")
    MechanicalDesignerDBFactory(name="Kunio Okawara", slug="kunio-okawara")
    WorkDBFactory(slug="mobile-suit-gundam", title="Mobile Suit Gundam")
    test_db_session.commit()


def slugs(search: CatalogSearch) -> dict[str, list[str]]:
    """Each kind's result slugs, keyed by the kind."""
    return {
        kind: [card["slug"] for card in cards]
        for kind, cards in search.results.model_dump().items()
    }


@pytest.mark.usefixtures("catalog")
class TestCatalogSearchFacadeSearch:
    @pytest.mark.parametrize(
        ("q", "matches"),
        [
            ("zeon", {"organizations": ["zeonic", "principality-of-zeon"]}),
            (
                "gundam",
                {"mobile_suits": ["rx-78-2-gundam"], "works": ["mobile-suit-gundam"]},
            ),
            ("MS-06", {"mobile_suits": ["zaku-ii"]}),
            ("okawara", {"mechanical_designers": ["kunio-okawara"]}),
            ("char", {"characters": ["char-aznable"]}),
            ("turn a", {}),
        ],
    )
    def test_search_matches_each_kind_as_its_list_does(
        self, test_db_session: Session, q: str, matches: dict[str, list[str]]
    ) -> None:
        """Prefix matches lead, as in each list: Zeonic first (D8)."""
        search = CatalogSearchFacade(db_session=test_db_session).search(q=q, limit=5)

        assert slugs(search) == NO_MATCHES | matches
        assert search.totals.model_dump() == {
            kind: len(found) for kind, found in (NO_MATCHES | matches).items()
        }

    def test_search_limits_each_kind_but_totals_every_match(
        self, test_db_session: Session
    ) -> None:
        search = CatalogSearchFacade(db_session=test_db_session).search(q="a", limit=1)

        assert slugs(search) == {
            "characters": ["amuro-ray"],
            "mechanical_designers": ["kunio-okawara"],
            "mobile_suits": ["act-zaku"],
            "organizations": ["earth-federation"],
            "works": ["mobile-suit-gundam"],
        }
        assert search.totals.model_dump() == {
            "characters": 2,
            "mechanical_designers": 1,
            "mobile_suits": 3,
            "organizations": 2,
            "works": 1,
        }

    @pytest.mark.parametrize("q", [None, "", " -- "])
    def test_search_blank_q_lists_the_first_rows(
        self, test_db_session: Session, q: str | None
    ) -> None:
        """A blank ``q`` is no filter (D8, Q4)."""
        search = CatalogSearchFacade(db_session=test_db_session).search(q=q, limit=2)

        assert slugs(search) == {
            "characters": ["amuro-ray", "char-aznable"],
            "mechanical_designers": ["kunio-okawara"],
            "mobile_suits": ["act-zaku", "rx-78-2-gundam"],
            "organizations": ["earth-federation", "principality-of-zeon"],
            "works": ["mobile-suit-gundam"],
        }
        assert search.totals.model_dump() == {
            "characters": 2,
            "mechanical_designers": 1,
            "mobile_suits": 3,
            "organizations": 3,
            "works": 1,
        }


@pytest.fixture
def related_catalog(test_db_session: Session) -> None:
    """One ``solo`` and three ``trio`` rows of every kind.

    Each suit and work has a continuity, and each organization a
    parent, so the cards' joined rows load while counting.
    """
    uc = ContinuityDBFactory(name="Universal Century", slug="universal-century")
    parent = OrganizationDBFactory(name="Parent", slug="parent")
    test_db_session.flush()
    for term, count in (("solo", 1), ("trio", 3)):
        for n in range(count):
            slug = f"{term}-{n}"
            MobileSuitDBFactory(continuity_id=uc.id, name=slug, slug=slug)
            CharacterDBFactory(name=slug, slug=slug)
            OrganizationDBFactory(
                name=slug, parent_organization_id=parent.id, slug=slug
            )
            MechanicalDesignerDBFactory(name=slug, slug=slug)
            WorkDBFactory(continuity_id=uc.id, slug=slug, title=slug)
    test_db_session.commit()


@pytest.mark.usefixtures("related_catalog")
class TestCatalogSearchFacadeStatementCount:
    def test_search_sends_ten_statements_however_many_rows_match(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """A page and a count per kind, at one row or three."""
        facade = CatalogSearchFacade(db_session=test_db_session)
        with count_statements() as one_each:
            solo = facade.search(q="solo", limit=5)
        with count_statements() as three_each:
            trio = facade.search(q="trio", limit=5)
        with count_statements() as blank:
            facade.search(q=None, limit=5)

        assert set(solo.totals.model_dump().values()) == {1}
        assert set(trio.totals.model_dump().values()) == {3}
        assert trio.results.mobile_suits[0].continuity is not None
        assert trio.results.organizations[0].parent_organization is not None
        assert one_each.value == three_each.value == blank.value == 10
