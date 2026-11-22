import uuid
from collections.abc import Sequence
from datetime import date, datetime

import pytest
from sqlalchemy.orm import Session

from _factories.character.db import CharacterDBFactory
from _factories.character_appearance.db import CharacterAppearanceDBFactory
from _factories.character_slug_redirect.db import CharacterSlugRedirectDBFactory
from _factories.continuity.db import ContinuityDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_appearance.db import MobileSuitAppearanceDBFactory
from _factories.mobile_suit_pilot.db import MobileSuitPilotDBFactory
from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from models._tests.query_count import CountStatements
from models.character.entity import CharacterCardEntity
from models.character.facade import CharacterFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc002")
ZETA_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc003")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc004")
AMURO_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc005")
BRIGHT_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc006")
KAI_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc007")
GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc008")
DIJEH_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc009")
NU_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc00a")
GUNCANNON_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc00b")


@pytest.fixture
def characters(test_db_session: Session) -> None:
    """Three characters, two works, and the suits Amuro and Kai pilot.

    Amuro is in both works and pilots a suit in each, plus one with no
    recorded work. Kai is in one work and pilots one suit. Bright pilots
    nothing.
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
    CharacterDBFactory(id=AMURO_ID, name="Amuro Ray", slug="amuro-ray")
    CharacterDBFactory(id=BRIGHT_ID, name="Bright Noa", slug="bright-noa")
    CharacterDBFactory(id=KAI_ID, name="Kai Shiden", slug="kai-shiden")
    MobileSuitDBFactory(id=GUNDAM_ID, continuity_id=UC_ID, name="Gundam", slug="gundam")
    MobileSuitDBFactory(id=DIJEH_ID, continuity_id=UC_ID, name="Dijeh", slug="dijeh")
    MobileSuitDBFactory(
        id=NU_ID, continuity_id=UC_ID, name="Nu Gundam", slug="nu-gundam"
    )
    MobileSuitDBFactory(
        id=GUNCANNON_ID, continuity_id=UC_ID, name="Guncannon", slug="guncannon"
    )
    test_db_session.flush()
    # Listed in reverse release order, so the read must sort them.
    for character_id, work_id in [
        (AMURO_ID, ZETA_ID),
        (AMURO_ID, MSG_ID),
        (KAI_ID, MSG_ID),
    ]:
        CharacterAppearanceDBFactory(
            character_id=character_id, source_id=SOURCE_ID, work_id=work_id
        )
    for suit_id, work_id in [
        (GUNDAM_ID, MSG_ID),
        (DIJEH_ID, ZETA_ID),
        (GUNCANNON_ID, MSG_ID),
    ]:
        MobileSuitAppearanceDBFactory(
            mobile_suit_id=suit_id, source_id=SOURCE_ID, work_id=work_id
        )
    test_db_session.flush()
    for character_id, suit_id, work_id in [
        (AMURO_ID, NU_ID, None),
        (AMURO_ID, DIJEH_ID, ZETA_ID),
        (AMURO_ID, GUNDAM_ID, MSG_ID),
        (KAI_ID, GUNCANNON_ID, MSG_ID),
    ]:
        MobileSuitPilotDBFactory(
            character_id=character_id,
            mobile_suit_id=suit_id,
            source_id=SOURCE_ID,
            work_id=work_id,
        )
    test_db_session.commit()


def slugs(page_items: Sequence[CharacterCardEntity]) -> list[str]:
    return [character.slug for character in page_items]


@pytest.mark.usefixtures("characters")
class TestCharacterFacadeGetPage:
    def test_get_page(self, test_db_session: Session) -> None:
        page = CharacterFacade(db_session=test_db_session).get_page(limit=50, offset=0)

        assert slugs(page.items) == ["amuro-ray", "bright-noa", "kai-shiden"]
        assert page.total == 3

    def test_get_page_limit_and_offset(self, test_db_session: Session) -> None:
        page = CharacterFacade(db_session=test_db_session).get_page(limit=1, offset=1)

        assert slugs(page.items) == ["bright-noa"]
        assert page.total == 3

    def test_get_page_past_the_end(self, test_db_session: Session) -> None:
        """An empty page still reports the real total (D3)."""
        page = CharacterFacade(db_session=test_db_session).get_page(limit=50, offset=10)

        assert page.items == []
        assert page.total == 3

    @pytest.mark.parametrize(
        ("work_slug", "expected"),
        [
            ("mobile-suit-gundam", ["amuro-ray", "kai-shiden"]),
            ("mobile-suit-zeta-gundam", ["amuro-ray"]),
            ("turn-a-gundam", []),
        ],
    )
    def test_get_page_filters_by_work(
        self, test_db_session: Session, work_slug: str, expected: list[str]
    ) -> None:
        page = CharacterFacade(db_session=test_db_session).get_page(
            work_slug=work_slug, limit=50, offset=0
        )

        assert slugs(page.items) == expected
        assert page.total == len(expected)

    def test_get_page_searches_slugs_prefix_first(
        self, test_db_session: Session
    ) -> None:
        """``noa`` is inside one slug; ``bright`` starts one (D8)."""
        facade = CharacterFacade(db_session=test_db_session)

        assert slugs(facade.get_page(q="Noa", limit=50, offset=0).items) == [
            "bright-noa"
        ]
        assert slugs(facade.get_page(q="a", limit=50, offset=0).items) == [
            "amuro-ray",
            "bright-noa",
            "kai-shiden",
        ]


@pytest.mark.usefixtures("characters")
class TestCharacterFacadeSlugs:
    def test_get_id_by_slug(self, test_db_session: Session) -> None:
        facade = CharacterFacade(db_session=test_db_session)

        assert facade.get_id_by_slug("amuro-ray") == AMURO_ID

    def test_get_id_by_slug_old_slug(self, test_db_session: Session) -> None:
        CharacterSlugRedirectDBFactory(old_slug="amuro", character_id=AMURO_ID)
        test_db_session.commit()

        facade = CharacterFacade(db_session=test_db_session)

        assert facade.get_id_by_slug("amuro") == AMURO_ID

    def test_get_id_by_slug_prefers_a_current_slug(
        self, test_db_session: Session
    ) -> None:
        """A redirect naming a current slug loses to it (D2)."""
        CharacterSlugRedirectDBFactory(old_slug="amuro-ray", character_id=KAI_ID)
        test_db_session.commit()

        facade = CharacterFacade(db_session=test_db_session)

        assert facade.get_id_by_slug("amuro-ray") == AMURO_ID

    def test_get_id_by_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(CharacterFacade.NotFoundError, match="slug='char-aznable'"):
            CharacterFacade(db_session=test_db_session).get_id_by_slug("char-aznable")


@pytest.mark.usefixtures("characters")
class TestCharacterFacadeGetOneBySlug:
    def test_get_one_by_slug(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        amuro = CharacterFacade(db_session=test_db_session).get_one_by_slug("amuro-ray")

        assert amuro.slug == "amuro-ray"
        assert [a.work.slug for a in amuro.appearances] == [
            "mobile-suit-gundam",
            "mobile-suit-zeta-gundam",
        ]
        assert amuro.appearances[0].work.continuity is not None
        assert amuro.appearances[0].source.url == "https://gundam.fandom.com/?curid=1"
        assert amuro.appearances[0].created_at == mock_utcnow

    def test_get_one_by_slug_orders_piloted_suits_by_work(
        self, test_db_session: Session
    ) -> None:
        """By release, not name; a suit with no work comes last (Q2)."""
        amuro = CharacterFacade(db_session=test_db_session).get_one_by_slug("amuro-ray")

        assert [
            (p.mobile_suit.slug, p.work.slug if p.work else None)
            for p in amuro.piloted_mobile_suits
        ] == [
            ("gundam", "mobile-suit-gundam"),
            ("dijeh", "mobile-suit-zeta-gundam"),
            ("nu-gundam", None),
        ]
        assert amuro.piloted_mobile_suits[0].work is not None
        assert amuro.piloted_mobile_suits[0].work.model_dump() == {
            "slug": "mobile-suit-gundam",
            "title": "Mobile Suit Gundam",
        }
        assert amuro.piloted_mobile_suits[0].mobile_suit.continuity is not None

    def test_get_one_by_slug_with_empty_lists(self, test_db_session: Session) -> None:
        bright = CharacterFacade(db_session=test_db_session).get_one_by_slug(
            "bright-noa"
        )

        assert bright.appearances == []
        assert bright.piloted_mobile_suits == []

    def test_get_one_by_slug_old_slug(self, test_db_session: Session) -> None:
        """It carries the current slug, so the URL can change."""
        CharacterSlugRedirectDBFactory(old_slug="amuro", character_id=AMURO_ID)
        test_db_session.commit()

        amuro = CharacterFacade(db_session=test_db_session).get_one_by_slug("amuro")

        assert amuro.slug == "amuro-ray"

    def test_get_one_by_slug_no_result(self, test_db_session: Session) -> None:
        with pytest.raises(CharacterFacade.NotFoundError, match="slug='char-aznable'"):
            CharacterFacade(db_session=test_db_session).get_one_by_slug("char-aznable")

    def test_get_one_by_slug_sends_three_statements(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """The character, works and suits, at 1 row or 5 (PYTEST-24).

        Kai has one work and one suit; Char gets five of each.
        """
        char = CharacterDBFactory(name="Char Aznable", slug="char-aznable")
        works = [WorkDBFactory(continuity_id=UC_ID) for _ in range(5)]
        suits = [MobileSuitDBFactory(continuity_id=UC_ID) for _ in range(5)]
        test_db_session.flush()
        for work, suit in zip(works, suits, strict=True):
            CharacterAppearanceDBFactory(
                character_id=char.id, source_id=SOURCE_ID, work_id=work.id
            )
            MobileSuitAppearanceDBFactory(
                mobile_suit_id=suit.id, source_id=SOURCE_ID, work_id=work.id
            )
        test_db_session.flush()
        for work, suit in zip(works, suits, strict=True):
            MobileSuitPilotDBFactory(
                character_id=char.id,
                mobile_suit_id=suit.id,
                source_id=SOURCE_ID,
                work_id=work.id,
            )
        test_db_session.commit()
        facade = CharacterFacade(db_session=test_db_session)

        with count_statements() as kai_statements:
            kai = facade.get_one_by_slug("kai-shiden")
        with count_statements() as char_statements:
            char_detail = facade.get_one_by_slug("char-aznable")

        assert (len(kai.appearances), len(kai.piloted_mobile_suits)) == (1, 1)
        assert (
            len(char_detail.appearances),
            len(char_detail.piloted_mobile_suits),
        ) == (5, 5)
        assert kai_statements.value == char_statements.value == 3


@pytest.mark.usefixtures("characters")
class TestCharacterFacadeWrites:
    def test_create_or_update(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        facade = CharacterFacade(db_session=test_db_session)
        payload = {
            "fandom_page_id": 1012,
            "name": "Amuro Ray",
            "name_ja": "アムロ・レイ",
            "slug": "amuro-ray",
        }

        updated = facade.create_or_update(payload=payload)
        rerun = facade.create_or_update(payload=payload)

        assert updated.id == AMURO_ID
        assert updated.fandom_page_id == 1012
        assert updated.updated_at != mock_utcnow
        assert rerun.updated_at == updated.updated_at

    def test_create_or_update_appearance(self, test_db_session: Session) -> None:
        new_source = SourceDBFactory()
        test_db_session.commit()

        appearance = CharacterFacade(
            db_session=test_db_session
        ).create_or_update_appearance(
            payload={
                "character_id": AMURO_ID,
                "source_id": new_source.id,
                "work_id": MSG_ID,
            }
        )

        assert appearance.source_id == new_source.id

    def test_create_or_update_slug_redirect(self, test_db_session: Session) -> None:
        CharacterSlugRedirectDBFactory(old_slug="amuro", character_id=KAI_ID)
        test_db_session.commit()

        redirect = CharacterFacade(
            db_session=test_db_session
        ).create_or_update_slug_redirect(
            payload={"character_id": AMURO_ID, "old_slug": "amuro"}
        )

        assert redirect.character_id == AMURO_ID
