import uuid
from collections.abc import Sequence
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from _factories.mechanical_designer_slug_redirect.db import (
    MechanicalDesignerSlugRedirectDBFactory,
)
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_designer.db import MobileSuitDesignerDBFactory
from _factories.source.db import SourceDBFactory
from models._tests.query_count import CountStatements
from models.mechanical_designer.entity import (
    MechanicalDesignerCardEntity,
    MechanicalDesignerDetailEntity,
)
from models.mechanical_designer.facade import MechanicalDesignerFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be101")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be102")
OKAWARA_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be103")
KATOKI_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be104")
KAWAHARA_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5be105")


@pytest.fixture
def designers(test_db_session: Session) -> None:
    """Three designers: Okawara with three suits, Katoki with one."""
    ContinuityDBFactory(id=UC_ID, name="Universal Century", slug="universal-century")
    SourceDBFactory(id=SOURCE_ID, url="https://gundam.fandom.com/?curid=1")
    MechanicalDesignerDBFactory(
        id=OKAWARA_ID, name="Kunio Okawara", slug="kunio-okawara"
    )
    MechanicalDesignerDBFactory(
        id=KATOKI_ID, name="Hajime Katoki", slug="hajime-katoki"
    )
    MechanicalDesignerDBFactory(
        id=KAWAHARA_ID, name="Masaki Kawahara", slug="masaki-kawahara"
    )
    suits = {
        slug: MobileSuitDBFactory(continuity_id=UC_ID, name=name, slug=slug).id
        for name, slug in [
            ("Zaku II", "zaku-ii"),
            ("Gundam", "gundam"),
            ("GM", "gm"),
        ]
    }
    test_db_session.flush()
    for designer_id, slug in [
        (OKAWARA_ID, "zaku-ii"),
        (OKAWARA_ID, "gundam"),
        (OKAWARA_ID, "gm"),
        (KATOKI_ID, "gundam"),
    ]:
        MobileSuitDesignerDBFactory(
            mechanical_designer_id=designer_id,
            mobile_suit_id=suits[slug],
            source_id=SOURCE_ID,
        )
    test_db_session.commit()


def slugs(page_items: Sequence[MechanicalDesignerCardEntity]) -> list[str]:
    return [designer.slug for designer in page_items]


@pytest.mark.usefixtures("designers")
class TestMechanicalDesignerFacadeGetPage:
    def test_get_page(self, test_db_session: Session) -> None:
        page = MechanicalDesignerFacade(db_session=test_db_session).get_page(
            limit=50, offset=0
        )

        assert slugs(page.items) == [
            "hajime-katoki",
            "kunio-okawara",
            "masaki-kawahara",
        ]
        assert page.total == 3

    def test_get_page_past_the_end(self, test_db_session: Session) -> None:
        page = MechanicalDesignerFacade(db_session=test_db_session).get_page(
            limit=50, offset=10
        )

        assert page.items == []
        assert page.total == 3

    def test_get_page_searches_slugs_prefix_first(
        self, test_db_session: Session
    ) -> None:
        """``k`` starts ``kunio-okawara`` and is in the others (D8)."""
        page = MechanicalDesignerFacade(db_session=test_db_session).get_page(
            q="K", limit=50, offset=0
        )

        assert slugs(page.items) == [
            "kunio-okawara",
            "hajime-katoki",
            "masaki-kawahara",
        ]

    def test_get_page_searches_names(self, test_db_session: Session) -> None:
        """A name the slug doesn't spell still matches (D8)."""
        MechanicalDesignerDBFactory(name="Yutaka Izubuchi", slug="izubuchi")
        test_db_session.commit()

        page = MechanicalDesignerFacade(db_session=test_db_session).get_page(
            q="yutaka", limit=50, offset=0
        )

        assert slugs(page.items) == ["izubuchi"]


@pytest.mark.usefixtures("designers")
class TestMechanicalDesignerFacadeGetOneBySlug:
    def test_get_one_by_slug(self, test_db_session: Session) -> None:
        """The detail entity; the suits are on a page of their own."""
        designer = MechanicalDesignerFacade(db_session=test_db_session).get_one_by_slug(
            "kunio-okawara"
        )

        assert isinstance(designer, MechanicalDesignerDetailEntity)
        assert designer.name == "Kunio Okawara"
        assert "mobile_suits" not in designer.model_dump()

    def test_get_one_by_slug_old_slug(self, test_db_session: Session) -> None:
        MechanicalDesignerSlugRedirectDBFactory(
            mechanical_designer_id=OKAWARA_ID, old_slug="okawara"
        )
        test_db_session.commit()

        facade = MechanicalDesignerFacade(db_session=test_db_session)

        assert facade.get_one_by_slug("okawara").slug == "kunio-okawara"
        assert facade.get_id_by_slug("okawara") == OKAWARA_ID

    def test_get_one_by_slug_prefers_a_current_slug(
        self, test_db_session: Session
    ) -> None:
        """A redirect naming a current slug loses to it (D2)."""
        MechanicalDesignerSlugRedirectDBFactory(
            mechanical_designer_id=KATOKI_ID, old_slug="kunio-okawara"
        )
        test_db_session.commit()

        facade = MechanicalDesignerFacade(db_session=test_db_session)

        assert facade.get_id_by_slug("kunio-okawara") == OKAWARA_ID

    def test_get_one_by_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(
            MechanicalDesignerFacade.NotFoundError, match="slug='yutaka-izubuchi'"
        ):
            MechanicalDesignerFacade(db_session=test_db_session).get_one_by_slug(
                "yutaka-izubuchi"
            )

    def test_get_id_by_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(
            MechanicalDesignerFacade.NotFoundError, match="slug='yutaka-izubuchi'"
        ):
            MechanicalDesignerFacade(db_session=test_db_session).get_id_by_slug(
                "yutaka-izubuchi"
            )


@pytest.mark.usefixtures("designers")
class TestMechanicalDesignerFacadeGetMobileSuitPage:
    def test_get_mobile_suit_page(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        page = MechanicalDesignerFacade(
            db_session=test_db_session
        ).get_mobile_suit_page("kunio-okawara", limit=2, offset=0)

        assert [item.mobile_suit.slug for item in page.items] == ["gm", "gundam"]
        assert page.total == 3
        assert page.items[0].mobile_suit.continuity is not None
        assert page.items[0].source.url == "https://gundam.fandom.com/?curid=1"
        assert page.items[0].created_at == mock_utcnow

    def test_get_mobile_suit_page_empty(self, test_db_session: Session) -> None:
        page = MechanicalDesignerFacade(
            db_session=test_db_session
        ).get_mobile_suit_page("masaki-kawahara", limit=50, offset=0)

        assert page.items == []
        assert page.total == 0

    def test_get_mobile_suit_page_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(
            MechanicalDesignerFacade.NotFoundError, match="slug='yutaka-izubuchi'"
        ):
            MechanicalDesignerFacade(db_session=test_db_session).get_mobile_suit_page(
                "yutaka-izubuchi", limit=50, offset=0
            )

    def test_get_mobile_suit_page_sends_three_statements(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """The slug, the page and the count, at 1 suit or 5 (PYTEST-24).

        Okawara has three suits in the fixture; two more make five.
        """
        for _ in range(2):
            suit = MobileSuitDBFactory(continuity_id=UC_ID)
            test_db_session.flush()
            MobileSuitDesignerDBFactory(
                mechanical_designer_id=OKAWARA_ID,
                mobile_suit_id=suit.id,
                source_id=SOURCE_ID,
            )
        test_db_session.commit()
        facade = MechanicalDesignerFacade(db_session=test_db_session)

        with count_statements() as one_suit:
            katoki = facade.get_mobile_suit_page("hajime-katoki", limit=50, offset=0)
        with count_statements() as five_suits:
            okawara = facade.get_mobile_suit_page("kunio-okawara", limit=50, offset=0)

        assert (len(katoki.items), len(okawara.items)) == (1, 5)
        assert one_suit.value == five_suits.value == 3


@pytest.mark.usefixtures("designers")
class TestMechanicalDesignerFacadeWrites:
    def test_create_or_update(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        facade = MechanicalDesignerFacade(db_session=test_db_session)
        payload = {
            "fandom_page_id": 2204,
            "name": "Kunio Okawara",
            "name_ja": "大河原邦男",
            "slug": "kunio-okawara",
        }

        updated = facade.create_or_update(payload=payload)
        rerun = facade.create_or_update(payload=payload)

        assert updated.id == OKAWARA_ID
        assert updated.fandom_page_id == 2204
        assert updated.updated_at != mock_utcnow
        assert rerun.updated_at == updated.updated_at

    def test_create_or_update_slug_redirect(self, test_db_session: Session) -> None:
        MechanicalDesignerSlugRedirectDBFactory(
            mechanical_designer_id=KATOKI_ID, old_slug="okawara"
        )
        test_db_session.commit()

        redirect = MechanicalDesignerFacade(
            db_session=test_db_session
        ).create_or_update_slug_redirect(
            payload={"mechanical_designer_id": OKAWARA_ID, "old_slug": "okawara"}
        )

        assert redirect.mechanical_designer_id == OKAWARA_ID
