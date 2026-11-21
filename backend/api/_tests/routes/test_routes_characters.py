import uuid
from datetime import date

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
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
from models.character.facade import CharacterFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7002")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7003")
AMURO_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7004")
GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7005")
NU_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7006")


@pytest.fixture
def characters(test_db_session: Session) -> None:
    """Amuro, in one work, piloting a suit in it and one in none."""
    ContinuityDBFactory(id=UC_ID, name="Universal Century", slug="universal-century")
    WorkDBFactory(
        id=MSG_ID,
        continuity_id=UC_ID,
        slug="mobile-suit-gundam",
        start_date=date(1979, 4, 7),
        title="Mobile Suit Gundam",
    )
    SourceDBFactory(id=SOURCE_ID, url="https://gundam.fandom.com/?curid=1")
    CharacterDBFactory(
        id=AMURO_ID, name="Amuro Ray", name_ja="アムロ・レイ", slug="amuro-ray"
    )
    CharacterDBFactory(name="Bright Noa", slug="bright-noa")
    MobileSuitDBFactory(id=GUNDAM_ID, continuity_id=UC_ID, name="Gundam", slug="gundam")
    MobileSuitDBFactory(
        id=NU_ID, continuity_id=UC_ID, name="Nu Gundam", slug="nu-gundam"
    )
    # The links below have no ORM relationship to order them after their
    # rows, so the rows are flushed first.
    test_db_session.flush()
    CharacterAppearanceDBFactory(
        character_id=AMURO_ID, source_id=SOURCE_ID, work_id=MSG_ID
    )
    MobileSuitAppearanceDBFactory(
        mobile_suit_id=GUNDAM_ID, source_id=SOURCE_ID, work_id=MSG_ID
    )
    CharacterSlugRedirectDBFactory(old_slug="amuro", character_id=AMURO_ID)
    test_db_session.flush()
    for suit_id, work_id in ((NU_ID, None), (GUNDAM_ID, MSG_ID)):
        MobileSuitPilotDBFactory(
            character_id=AMURO_ID,
            mobile_suit_id=suit_id,
            source_id=SOURCE_ID,
            work_id=work_id,
        )
    test_db_session.commit()


@pytest.mark.usefixtures("characters")
class TestReadCharactersList:
    def test_returns_a_page(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/characters")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert [c["slug"] for c in body["data"]] == ["amuro-ray", "bright-noa"]
        assert set(body["data"][0]) == {
            "created_at",
            "name",
            "name_ja",
            "slug",
            "updated_at",
        }
        assert body["meta"] == {"limit": 50, "offset": 0, "total": 2}

    @pytest.mark.parametrize(
        ("query", "slugs", "total"),
        [
            ("?work=mobile-suit-gundam", ["amuro-ray"], 1),
            ("?work=turn-a-gundam", [], 0),
            ("?q=Bright", ["bright-noa"], 1),
            ("?limit=1&offset=1", ["bright-noa"], 2),
            ("?offset=10", [], 2),
        ],
    )
    def test_filters_and_pages(
        self, test_app_client: TestClient, query: str, slugs: list[str], total: int
    ) -> None:
        response = test_app_client.get(f"/api/characters{query}")

        assert response.status_code == status.HTTP_200_OK
        assert [c["slug"] for c in response.json()["data"]] == slugs
        assert response.json()["meta"]["total"] == total

    @pytest.mark.parametrize(
        "query", ["?limit=0", "?limit=101", "?offset=-1", f"?q={'a' * 101}"]
    )
    def test_rejects_bad_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(f"/api/characters{query}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            CharacterFacade, "get_page", autospec=True, side_effect=RuntimeError
        )

        response = test_app_client.get("/api/characters")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching characters"}


@pytest.mark.usefixtures("characters")
class TestReadCharacter:
    def test_returns_their_works_and_suits(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/characters/amuro-ray")

        assert response.status_code == status.HTTP_200_OK
        amuro = response.json()["data"]
        assert amuro["name_ja"] == "アムロ・レイ"
        [appearance] = amuro["appearances"]
        assert appearance["work"]["slug"] == "mobile-suit-gundam"
        assert appearance["source"]["url"] == "https://gundam.fandom.com/?curid=1"
        assert [
            (p["mobile_suit"]["slug"], p["work"]) for p in amuro["piloted_mobile_suits"]
        ] == [
            (
                "gundam",
                {"slug": "mobile-suit-gundam", "title": "Mobile Suit Gundam"},
            ),
            ("nu-gundam", None),
        ]

    def test_old_slug_returns_the_current_one(
        self, test_app_client: TestClient
    ) -> None:
        response = test_app_client.get("/api/characters/amuro")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["slug"] == "amuro-ray"

    def test_unknown_slug(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/characters/char-aznable")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Character not found"}

    @pytest.mark.parametrize("slug", ["Amuro-Ray", "amuro_ray", "-amuro"])
    def test_malformed_slug(self, test_app_client: TestClient, slug: str) -> None:
        response = test_app_client.get(f"/api/characters/{slug}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            CharacterFacade, "get_one_by_slug", autospec=True, side_effect=RuntimeError
        )

        response = test_app_client.get("/api/characters/amuro-ray")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching character"}
