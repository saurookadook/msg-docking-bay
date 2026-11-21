import uuid
from datetime import date, datetime

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_appearance.db import MobileSuitAppearanceDBFactory
from _factories.mobile_suit_organization.db import MobileSuitOrganizationDBFactory
from _factories.organization.db import OrganizationDBFactory
from _factories.organization_appearance.db import OrganizationAppearanceDBFactory
from _factories.organization_slug_redirect.db import (
    OrganizationSlugRedirectDBFactory,
)
from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from constants.catalog import MobileSuitOrganizationRole
from models._tests.query_count import CountStatements
from models.mobile_suit.entity import OrganizationMobileSuitEntity
from models.organization.db import OrganizationDB
from models.organization.entity import OrganizationCardEntity
from models.organization.facade import OrganizationFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd002")
ZETA_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd003")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd004")
EF_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd005")
TITANS_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd006")
LONDO_BELL_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd007")
ZEONIC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd008")
GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd009")
GM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd00a")
MK_II_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd00b")
ZAKU_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd00c")

OPERATOR = MobileSuitOrganizationRole.OPERATOR
DEVELOPER = MobileSuitOrganizationRole.DEVELOPER
MANUFACTURER = MobileSuitOrganizationRole.MANUFACTURER


@pytest.fixture
def organizations(test_db_session: Session) -> None:
    """Four organizations, two of them Federation units, and four suits.

    The Federation operates three suits, one in two works and one in no
    recorded work, and develops one of them. Zeonic builds the Zaku.
    """
    ContinuityDBFactory(id=UC_ID, name="Universal Century", slug="universal-century")
    WorkDBFactory(
        id=MSG_ID,
        continuity_id=UC_ID,
        slug="mobile-suit-gundam",
        start_date=date(1979, 4, 7),
        title="Mobile Suit Gundam",
    )
    WorkDBFactory(
        id=ZETA_ID,
        continuity_id=UC_ID,
        slug="mobile-suit-zeta-gundam",
        start_date=date(1985, 3, 2),
        title="Mobile Suit Zeta Gundam",
    )
    SourceDBFactory(id=SOURCE_ID, url="https://gundam.fandom.com/?curid=1")
    OrganizationDBFactory(id=EF_ID, name="Earth Federation", slug="earth-federation")
    OrganizationDBFactory(
        id=TITANS_ID, name="Titans", parent_organization_id=EF_ID, slug="titans"
    )
    OrganizationDBFactory(
        id=LONDO_BELL_ID,
        name="Londo Bell",
        parent_organization_id=EF_ID,
        slug="londo-bell",
    )
    OrganizationDBFactory(id=ZEONIC_ID, name="Zeonic", slug="zeonic")
    for suit_id, name, slug in [
        (GUNDAM_ID, "Gundam", "gundam"),
        (GM_ID, "GM", "gm"),
        (MK_II_ID, "Gundam Mk-II", "gundam-mk-ii"),
        (ZAKU_ID, "Zaku II", "zaku-ii"),
    ]:
        MobileSuitDBFactory(id=suit_id, continuity_id=UC_ID, name=name, slug=slug)
    test_db_session.flush()
    # Listed in reverse release order, so the read must sort them.
    for organization_id, work_id in [
        (EF_ID, ZETA_ID),
        (EF_ID, MSG_ID),
        (TITANS_ID, ZETA_ID),
        (ZEONIC_ID, MSG_ID),
    ]:
        OrganizationAppearanceDBFactory(
            organization_id=organization_id, source_id=SOURCE_ID, work_id=work_id
        )
    for suit_id, work_id in [
        (GUNDAM_ID, MSG_ID),
        (GM_ID, MSG_ID),
        (GM_ID, ZETA_ID),
        (MK_II_ID, ZETA_ID),
        (ZAKU_ID, MSG_ID),
    ]:
        MobileSuitAppearanceDBFactory(
            mobile_suit_id=suit_id, source_id=SOURCE_ID, work_id=work_id
        )
    test_db_session.flush()
    for suit_id, organization_id, role, work_id in [
        (GM_ID, EF_ID, OPERATOR, ZETA_ID),
        (GM_ID, EF_ID, OPERATOR, MSG_ID),
        (GUNDAM_ID, EF_ID, DEVELOPER, MSG_ID),
        (GUNDAM_ID, EF_ID, OPERATOR, MSG_ID),
        (MK_II_ID, EF_ID, OPERATOR, None),
        (MK_II_ID, TITANS_ID, DEVELOPER, ZETA_ID),
        (ZAKU_ID, ZEONIC_ID, MANUFACTURER, MSG_ID),
    ]:
        MobileSuitOrganizationDBFactory(
            mobile_suit_id=suit_id,
            organization_id=organization_id,
            role=role,
            source_id=SOURCE_ID,
            work_id=work_id,
        )
    test_db_session.commit()


def slugs(page_items: list[OrganizationCardEntity]) -> list[str]:
    return [organization.slug for organization in page_items]


def suit_slugs(page_items: list[OrganizationMobileSuitEntity]) -> list[str]:
    return [item.mobile_suit.slug for item in page_items]


@pytest.mark.usefixtures("organizations")
class TestOrganizationFacadeGetPage:
    def test_get_page(self, test_db_session: Session) -> None:
        page = OrganizationFacade(db_session=test_db_session).get_page(
            limit=50, offset=0
        )

        assert slugs(page.items) == [
            "earth-federation",
            "londo-bell",
            "titans",
            "zeonic",
        ]
        assert page.total == 4
        assert page.items[0].parent_organization is None
        assert page.items[2].parent_organization is not None
        assert page.items[2].parent_organization.model_dump() == {
            "name": "Earth Federation",
            "slug": "earth-federation",
        }

    def test_get_page_past_the_end(self, test_db_session: Session) -> None:
        """An empty page still reports the real total (D3)."""
        page = OrganizationFacade(db_session=test_db_session).get_page(
            limit=50, offset=10
        )

        assert page.items == []
        assert page.total == 4

    @pytest.mark.parametrize(
        ("filters", "expected"),
        [
            ({"work_slug": "mobile-suit-gundam"}, ["earth-federation", "zeonic"]),
            ({"work_slug": "mobile-suit-zeta-gundam"}, ["earth-federation", "titans"]),
            ({"work_slug": "turn-a-gundam"}, []),
            ({"q": "bell"}, ["londo-bell"]),
            ({"q": "o"}, ["earth-federation", "londo-bell", "zeonic"]),
        ],
    )
    def test_get_page_filters(
        self, test_db_session: Session, filters: dict[str, str], expected: list[str]
    ) -> None:
        page = OrganizationFacade(db_session=test_db_session).get_page(
            **filters, limit=50, offset=0
        )

        assert slugs(page.items) == expected
        assert page.total == len(expected)

    def test_get_page_search_ranks_prefix_matches_first(
        self, test_db_session: Session
    ) -> None:
        """``ti`` starts ``titans`` and is in ``federation`` (D8)."""
        page = OrganizationFacade(db_session=test_db_session).get_page(
            q="ti", limit=50, offset=0
        )

        assert slugs(page.items) == ["titans", "earth-federation"]


@pytest.mark.usefixtures("organizations")
class TestOrganizationFacadeSlugs:
    def test_get_id_by_slug_old_slug(self, test_db_session: Session) -> None:
        OrganizationSlugRedirectDBFactory(old_slug="efsf", organization_id=EF_ID)
        test_db_session.commit()

        facade = OrganizationFacade(db_session=test_db_session)

        assert facade.get_id_by_slug("efsf") == EF_ID

    def test_get_id_by_slug_prefers_a_current_slug(
        self, test_db_session: Session
    ) -> None:
        """A redirect naming a current slug loses to it (D2)."""
        OrganizationSlugRedirectDBFactory(old_slug="titans", organization_id=EF_ID)
        test_db_session.commit()

        facade = OrganizationFacade(db_session=test_db_session)

        assert facade.get_id_by_slug("titans") == TITANS_ID

    def test_get_id_by_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(OrganizationFacade.NotFoundError, match="slug='aeug'"):
            OrganizationFacade(db_session=test_db_session).get_id_by_slug("aeug")


@pytest.mark.usefixtures("organizations")
class TestOrganizationFacadeGetOneBySlug:
    def test_get_one_by_slug(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        federation = OrganizationFacade(db_session=test_db_session).get_one_by_slug(
            "earth-federation"
        )

        assert federation.parent_organization is None
        assert [child.model_dump() for child in federation.child_organizations] == [
            {"name": "Londo Bell", "slug": "londo-bell"},
            {"name": "Titans", "slug": "titans"},
        ]
        assert [a.work.slug for a in federation.appearances] == [
            "mobile-suit-gundam",
            "mobile-suit-zeta-gundam",
        ]
        assert federation.appearances[0].work.continuity is not None
        assert federation.appearances[0].source.url == (
            "https://gundam.fandom.com/?curid=1"
        )
        assert federation.appearances[0].created_at == mock_utcnow

    def test_get_one_by_slug_names_its_parent(self, test_db_session: Session) -> None:
        titans = OrganizationFacade(db_session=test_db_session).get_one_by_slug(
            "titans"
        )

        assert titans.parent_organization is not None
        assert titans.parent_organization.slug == "earth-federation"
        assert titans.child_organizations == []

    def test_get_one_by_slug_old_slug(self, test_db_session: Session) -> None:
        """It carries the current slug, so the URL can change."""
        OrganizationSlugRedirectDBFactory(old_slug="efsf", organization_id=EF_ID)
        test_db_session.commit()

        federation = OrganizationFacade(db_session=test_db_session).get_one_by_slug(
            "efsf"
        )

        assert federation.slug == "earth-federation"

    def test_get_one_by_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(OrganizationFacade.NotFoundError):
            OrganizationFacade(db_session=test_db_session).get_one_by_slug("aeug")

    def test_get_one_by_slug_sends_three_statements(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """The organization, its units and its works (PYTEST-24)."""
        facade = OrganizationFacade(db_session=test_db_session)
        with count_statements() as few:
            facade.get_one_by_slug("titans")
        with count_statements() as several:
            facade.get_one_by_slug("earth-federation")

        assert few.value == several.value == 3


@pytest.mark.usefixtures("organizations")
class TestOrganizationFacadeGetMobileSuitPage:
    def test_get_mobile_suit_page(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """One item per suit, by name, with every link it has (Q7)."""
        page = OrganizationFacade(db_session=test_db_session).get_mobile_suit_page(
            "earth-federation", limit=50, offset=0
        )

        assert suit_slugs(page.items) == ["gm", "gundam", "gundam-mk-ii"]
        assert page.total == 3
        assert page.items[0].mobile_suit.continuity is not None
        link = page.items[0].links[0]
        assert link.source.url == "https://gundam.fandom.com/?curid=1"
        assert link.created_at == mock_utcnow

    def test_get_mobile_suit_page_orders_links(self, test_db_session: Session) -> None:
        """By role, then release; a link with no work is last (Q2)."""
        page = OrganizationFacade(db_session=test_db_session).get_mobile_suit_page(
            "earth-federation", limit=50, offset=0
        )

        assert [
            [(link.role, link.work.slug if link.work else None) for link in item.links]
            for item in page.items
        ] == [
            [
                (OPERATOR, "mobile-suit-gundam"),
                (OPERATOR, "mobile-suit-zeta-gundam"),
            ],
            [
                (OPERATOR, "mobile-suit-gundam"),
                (DEVELOPER, "mobile-suit-gundam"),
            ],
            [(OPERATOR, None)],
        ]

    def test_get_mobile_suit_page_counts_suits_not_links(
        self, test_db_session: Session
    ) -> None:
        """Five links, three suits: the page and total are of suits."""
        page = OrganizationFacade(db_session=test_db_session).get_mobile_suit_page(
            "earth-federation", limit=1, offset=1
        )

        assert suit_slugs(page.items) == ["gundam"]
        assert len(page.items[0].links) == 2
        assert page.total == 3

    def test_get_mobile_suit_page_filters_suits_and_links_by_role(
        self, test_db_session: Session
    ) -> None:
        """The Gundam's operator link is left out too (Q9)."""
        page = OrganizationFacade(db_session=test_db_session).get_mobile_suit_page(
            "earth-federation", role=DEVELOPER, limit=50, offset=0
        )

        assert suit_slugs(page.items) == ["gundam"]
        assert [link.role for link in page.items[0].links] == [DEVELOPER]
        assert page.total == 1

    def test_get_mobile_suit_page_past_the_end(self, test_db_session: Session) -> None:
        page = OrganizationFacade(db_session=test_db_session).get_mobile_suit_page(
            "earth-federation", limit=50, offset=10
        )

        assert page.items == []
        assert page.total == 3

    def test_get_mobile_suit_page_old_slug(self, test_db_session: Session) -> None:
        OrganizationSlugRedirectDBFactory(old_slug="efsf", organization_id=EF_ID)
        test_db_session.commit()

        page = OrganizationFacade(db_session=test_db_session).get_mobile_suit_page(
            "efsf", limit=50, offset=0
        )

        assert page.total == 3

    def test_get_mobile_suit_page_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(OrganizationFacade.NotFoundError):
            OrganizationFacade(db_session=test_db_session).get_mobile_suit_page(
                "aeug", limit=50, offset=0
            )

    def test_get_mobile_suit_page_sends_four_statements(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """The slug, the page, the count and the links (PYTEST-24)."""
        facade = OrganizationFacade(db_session=test_db_session)
        with count_statements() as one_link:
            facade.get_mobile_suit_page("zeonic", limit=50, offset=0)
        with count_statements() as five_links:
            facade.get_mobile_suit_page("earth-federation", limit=50, offset=0)
        with count_statements() as empty_page:
            facade.get_mobile_suit_page("earth-federation", limit=50, offset=10)

        assert one_link.value == five_links.value == 4
        assert empty_page.value == 3


@pytest.mark.usefixtures("organizations")
class TestOrganizationFacadeWrites:
    def test_create_or_update(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        facade = OrganizationFacade(db_session=test_db_session)
        payload = {
            "fandom_page_id": 3307,
            "name": "Titans",
            "parent_organization_id": EF_ID,
            "slug": "titans",
        }

        updated = facade.create_or_update(payload=payload)
        rerun = facade.create_or_update(payload=payload)

        assert updated.id == TITANS_ID
        assert updated.fandom_page_id == 3307
        assert updated.updated_at != mock_utcnow
        assert rerun.updated_at == updated.updated_at

    def test_create_or_update_appearance(self, test_db_session: Session) -> None:
        new_source = SourceDBFactory()
        test_db_session.commit()

        appearance = OrganizationFacade(
            db_session=test_db_session
        ).create_or_update_appearance(
            payload={
                "organization_id": EF_ID,
                "source_id": new_source.id,
                "work_id": MSG_ID,
            }
        )

        assert appearance.source_id == new_source.id

    def test_create_or_update_slug_redirect(self, test_db_session: Session) -> None:
        OrganizationSlugRedirectDBFactory(old_slug="efsf", organization_id=TITANS_ID)
        test_db_session.commit()

        redirect = OrganizationFacade(
            db_session=test_db_session
        ).create_or_update_slug_redirect(
            payload={"old_slug": "efsf", "organization_id": EF_ID}
        )

        assert redirect.organization_id == EF_ID


class TestOrganizationCardEntity:
    def test_fails_on_a_row_whose_parent_was_not_loaded(
        self, test_db_session: Session
    ) -> None:
        """PYD-3: a missing eager load fails, not lazily queries."""
        OrganizationDBFactory()
        test_db_session.commit()
        test_db_session.expunge_all()
        row = test_db_session.scalars(select(OrganizationDB)).one()

        with pytest.raises(ValidationError, match="get_attribute_error"):
            OrganizationCardEntity.model_validate(row)
