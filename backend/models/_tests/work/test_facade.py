import uuid
from datetime import date, datetime
from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from _factories.work_relation.db import WorkRelationDBFactory
from _factories.work_slug_redirect.db import WorkSlugRedirectDBFactory
from constants.catalog import WorkRelationType, WorkType
from models._tests.query_count import CountStatements
from models.work.db import WorkDB
from models.work.entity import WorkCardEntity
from models.work.facade import WorkFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be002")
MOVIE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be003")
ZETA_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be004")
UNDATED_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be005")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be006")


@pytest.fixture
def works(test_db_session: Session) -> None:
    """Four works: three UC releases in date order, and one undated."""
    ContinuityDBFactory(id=UC_ID, name="Universal Century", slug="universal-century")
    WorkDBFactory(
        id=MSG_ID,
        continuity_id=UC_ID,
        slug="mobile-suit-gundam",
        start_date=date(1979, 4, 7),
        title="Mobile Suit Gundam",
    )
    WorkDBFactory(
        id=MOVIE_ID,
        continuity_id=UC_ID,
        parent_work_id=MSG_ID,
        slug="mobile-suit-gundam-i",
        start_date=date(1981, 3, 14),
        title="Mobile Suit Gundam I",
        work_type=WorkType.FILM,
    )
    WorkDBFactory(
        id=ZETA_ID,
        continuity_id=UC_ID,
        slug="mobile-suit-zeta-gundam",
        start_date=date(1985, 3, 2),
        title="Mobile Suit Zeta Gundam",
    )
    WorkDBFactory(id=UNDATED_ID, slug="gundam-untitled", title="Gundam Untitled")
    test_db_session.commit()


@pytest.fixture
def relations(test_db_session: Session, works: None) -> None:
    """The film compiles the series, and Zeta is its sequel."""
    SourceDBFactory(id=SOURCE_ID, url="https://gundam.fandom.com/?curid=1")
    WorkRelationDBFactory(
        from_work_id=MOVIE_ID,
        relation_type=WorkRelationType.COMPILATION_OF,
        source_id=SOURCE_ID,
        to_work_id=MSG_ID,
    )
    WorkRelationDBFactory(
        from_work_id=ZETA_ID,
        relation_type=WorkRelationType.SEQUEL_OF,
        source_id=SOURCE_ID,
        to_work_id=MSG_ID,
    )
    test_db_session.commit()


def slugs(page_items: list[WorkCardEntity]) -> list[str]:
    return [work.slug for work in page_items]


@pytest.mark.usefixtures("works")
class TestWorkFacadeGetPage:
    def test_get_page(self, test_db_session: Session) -> None:
        """First released first; a work with no date comes last."""
        page = WorkFacade(db_session=test_db_session).get_page(limit=50, offset=0)

        assert slugs(page.items) == [
            "mobile-suit-gundam",
            "mobile-suit-gundam-i",
            "mobile-suit-zeta-gundam",
            "gundam-untitled",
        ]
        assert page.total == 4
        assert page.items[0].continuity is not None
        assert page.items[0].continuity.slug == "universal-century"

    def test_get_page_limit_and_offset(self, test_db_session: Session) -> None:
        page = WorkFacade(db_session=test_db_session).get_page(limit=2, offset=1)

        assert slugs(page.items) == ["mobile-suit-gundam-i", "mobile-suit-zeta-gundam"]
        assert page.total == 4

    def test_get_page_past_the_end(self, test_db_session: Session) -> None:
        """An empty page still reports the real total (D3)."""
        page = WorkFacade(db_session=test_db_session).get_page(limit=50, offset=10)

        assert page.items == []
        assert page.total == 4

    @pytest.mark.parametrize(
        ("filters", "expected"),
        [
            (
                {"continuity_slug": "universal-century"},
                [
                    "mobile-suit-gundam",
                    "mobile-suit-gundam-i",
                    "mobile-suit-zeta-gundam",
                ],
            ),
            ({"work_type": WorkType.FILM}, ["mobile-suit-gundam-i"]),
            (
                {"continuity_slug": "universal-century", "work_type": WorkType.OVA},
                [],
            ),
            ({"continuity_slug": "cosmic-era"}, []),
        ],
    )
    def test_get_page_filters(
        self,
        test_db_session: Session,
        filters: dict[str, Any],
        expected: list[str],
    ) -> None:
        page = WorkFacade(db_session=test_db_session).get_page(
            **filters,
            limit=50,
            offset=0,
        )

        assert slugs(page.items) == expected
        assert page.total == len(expected)


class TestWorkFacadeGetPageOrder:
    def test_get_page_breaks_ties_by_id(self, test_db_session: Session) -> None:
        later = uuid.UUID("019a1984-0750-7142-aedd-75291c5be0f2")
        earlier = uuid.UUID("019a1984-0750-7142-aedd-75291c5be0f1")
        WorkDBFactory(id=later, slug="gundam-b", title="Gundam")
        WorkDBFactory(id=earlier, slug="gundam-a", title="Gundam")
        test_db_session.commit()

        page = WorkFacade(db_session=test_db_session).get_page(limit=50, offset=0)

        assert slugs(page.items) == ["gundam-a", "gundam-b"]


@pytest.mark.usefixtures("works")
class TestWorkFacadeSlugs:
    def test_get_id_by_slug(self, test_db_session: Session) -> None:
        facade = WorkFacade(db_session=test_db_session)

        assert facade.get_id_by_slug("mobile-suit-gundam") == MSG_ID

    def test_get_id_by_slug_old_slug(self, test_db_session: Session) -> None:
        WorkSlugRedirectDBFactory(old_slug="gundam-0079", work_id=MSG_ID)
        test_db_session.commit()

        assert (
            WorkFacade(db_session=test_db_session).get_id_by_slug("gundam-0079")
            == MSG_ID
        )

    def test_get_id_by_slug_prefers_a_current_slug(
        self, test_db_session: Session
    ) -> None:
        """A redirect naming a current slug loses to it (D2)."""
        WorkSlugRedirectDBFactory(old_slug="mobile-suit-gundam", work_id=ZETA_ID)
        test_db_session.commit()

        facade = WorkFacade(db_session=test_db_session)

        assert facade.get_id_by_slug("mobile-suit-gundam") == MSG_ID

    def test_get_id_by_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(WorkFacade.NotFoundError, match="slug='turn-a-gundam'"):
            WorkFacade(db_session=test_db_session).get_id_by_slug("turn-a-gundam")


@pytest.mark.usefixtures("relations")
class TestWorkFacadeGetOneBySlug:
    def test_get_one_by_slug(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        work = WorkFacade(db_session=test_db_session).get_one_by_slug(
            "mobile-suit-gundam-i"
        )

        assert work.slug == "mobile-suit-gundam-i"
        assert work.work_type is WorkType.FILM
        assert work.parent_work is not None
        assert work.parent_work.model_dump() == {
            "slug": "mobile-suit-gundam",
            "title": "Mobile Suit Gundam",
        }
        assert [
            r.model_dump(include={"direction", "relation_type"}) for r in work.relations
        ] == [
            {"direction": "outgoing", "relation_type": WorkRelationType.COMPILATION_OF}
        ]
        assert work.relations[0].work.slug == "mobile-suit-gundam"
        assert work.relations[0].source.url == "https://gundam.fandom.com/?curid=1"
        assert work.relations[0].created_at == mock_utcnow

    def test_get_one_by_slug_reads_relations_from_its_side(
        self, test_db_session: Session
    ) -> None:
        """Ordered by type (enum order), then direction, then title."""
        work = WorkFacade(db_session=test_db_session).get_one_by_slug(
            "mobile-suit-gundam"
        )

        assert work.parent_work is None
        assert [
            (r.relation_type, r.direction, r.work.slug) for r in work.relations
        ] == [
            (WorkRelationType.SEQUEL_OF, "incoming", "mobile-suit-zeta-gundam"),
            (WorkRelationType.COMPILATION_OF, "incoming", "mobile-suit-gundam-i"),
        ]

    def test_get_one_by_slug_old_slug(self, test_db_session: Session) -> None:
        """It carries the current slug, so the URL can change."""
        WorkSlugRedirectDBFactory(old_slug="gundam-0079", work_id=MSG_ID)
        test_db_session.commit()

        work = WorkFacade(db_session=test_db_session).get_one_by_slug("gundam-0079")

        assert work.slug == "mobile-suit-gundam"

    def test_get_one_by_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(WorkFacade.NotFoundError):
            WorkFacade(db_session=test_db_session).get_one_by_slug("turn-a-gundam")

    def test_get_one_by_slug_sends_two_statements(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """The work, then its relations, at any count (PYTEST-24)."""
        facade = WorkFacade(db_session=test_db_session)
        with count_statements() as one_relation:
            facade.get_one_by_slug("mobile-suit-zeta-gundam")
        with count_statements() as two_relations:
            facade.get_one_by_slug("mobile-suit-gundam")

        assert one_relation.value == two_relations.value == 2


@pytest.mark.usefixtures("works")
class TestWorkFacadeWrites:
    def test_create_or_update(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        facade = WorkFacade(db_session=test_db_session)

        updated = facade.create_or_update(
            payload={
                "slug": "mobile-suit-gundam",
                "title": "Mobile Suit Gundam",
                "work_type": WorkType.TV_SERIES,
                "fandom_page_id": 2001,
            }
        )
        rerun = facade.create_or_update(
            payload={
                "slug": "mobile-suit-gundam",
                "title": "Mobile Suit Gundam",
                "work_type": WorkType.TV_SERIES,
                "fandom_page_id": 2001,
            }
        )

        assert updated.id == MSG_ID
        assert updated.fandom_page_id == 2001
        assert updated.updated_at != mock_utcnow
        assert rerun.updated_at == updated.updated_at

    def test_create_or_update_relation(self, test_db_session: Session) -> None:
        old_source = SourceDBFactory()
        new_source = SourceDBFactory()
        WorkRelationDBFactory(
            from_work_id=ZETA_ID,
            relation_type=WorkRelationType.SEQUEL_OF,
            source_id=old_source.id,
            to_work_id=MSG_ID,
        )
        test_db_session.commit()

        relation = WorkFacade(db_session=test_db_session).create_or_update_relation(
            payload={
                "from_work_id": ZETA_ID,
                "relation_type": WorkRelationType.SEQUEL_OF,
                "source_id": new_source.id,
                "to_work_id": MSG_ID,
            }
        )

        assert relation.source_id == new_source.id

    def test_create_or_update_slug_redirect(self, test_db_session: Session) -> None:
        WorkSlugRedirectDBFactory(old_slug="gundam-0079", work_id=ZETA_ID)
        test_db_session.commit()

        redirect = WorkFacade(
            db_session=test_db_session
        ).create_or_update_slug_redirect(
            payload={"old_slug": "gundam-0079", "work_id": MSG_ID}
        )

        assert redirect.work_id == MSG_ID


class TestWorkCardEntity:
    def test_fails_on_a_row_whose_continuity_was_not_loaded(
        self, test_db_session: Session
    ) -> None:
        WorkDBFactory()
        test_db_session.commit()
        test_db_session.expunge_all()
        row = test_db_session.scalars(select(WorkDB)).one()

        with pytest.raises(ValidationError, match="get_attribute_error"):
            WorkCardEntity.model_validate(row)
