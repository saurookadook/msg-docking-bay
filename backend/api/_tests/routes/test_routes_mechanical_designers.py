import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from _factories.mechanical_designer_slug_redirect.db import (
    MechanicalDesignerSlugRedirectDBFactory,
)
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_designer.db import MobileSuitDesignerDBFactory
from _factories.source.db import SourceDBFactory
from models.mechanical_designer.facade import MechanicalDesignerFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b9001")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b9002")
OKAWARA_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b9003")


@pytest.fixture
def designers(test_db_session: Session) -> None:
    """Okawara, credited with two suits, and Katoki, with none."""
    ContinuityDBFactory(id=UC_ID, name="Universal Century", slug="universal-century")
    SourceDBFactory(id=SOURCE_ID, url="https://gundam.fandom.com/?curid=1")
    MechanicalDesignerDBFactory(
        id=OKAWARA_ID, name="Kunio Okawara", name_ja="大河原邦男", slug="kunio-okawara"
    )
    MechanicalDesignerDBFactory(name="Hajime Katoki", slug="hajime-katoki")
    suit_ids = [
        MobileSuitDBFactory(continuity_id=UC_ID, name=name, slug=slug).id
        for name, slug in (("Zaku II", "zaku-ii"), ("Gundam", "gundam"))
    ]
    # NOTE: the credits below have no ORM relationship to order them
    # after their rows, so the rows are flushed first.
    test_db_session.flush()
    MechanicalDesignerSlugRedirectDBFactory(
        mechanical_designer_id=OKAWARA_ID, old_slug="okawara"
    )
    for suit_id in suit_ids:
        MobileSuitDesignerDBFactory(
            mechanical_designer_id=OKAWARA_ID,
            mobile_suit_id=suit_id,
            source_id=SOURCE_ID,
        )
    test_db_session.commit()


@pytest.mark.usefixtures("designers")
class TestReadMechanicalDesignersList:
    def test_returns_a_page(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/mechanical-designers")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert [d["slug"] for d in body["data"]] == ["hajime-katoki", "kunio-okawara"]
        assert "id" not in body["data"][0]
        assert body["meta"] == {"limit": 50, "offset": 0, "total": 2}

    @pytest.mark.parametrize(
        ("query", "slugs", "total"),
        [
            ("?q=okawara", ["kunio-okawara"], 1),
            ("?q=tomino", [], 0),
            ("?limit=1&offset=1", ["kunio-okawara"], 2),
        ],
    )
    def test_filters_and_pages(
        self, test_app_client: TestClient, query: str, slugs: list[str], total: int
    ) -> None:
        response = test_app_client.get(f"/api/mechanical-designers{query}")

        assert response.status_code == status.HTTP_200_OK
        assert [d["slug"] for d in response.json()["data"]] == slugs
        assert response.json()["meta"]["total"] == total

    @pytest.mark.parametrize(
        "query",
        [
            # the largest accepted values
            "?limit=100",
            f"?q={'a' * 100}",
            # the smallest accepted values
            "?limit=1&offset=0",
        ],
    )
    def test_accepts_boundary_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(f"/api/mechanical-designers{query}")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "query",
        [
            # one past the largest accepted values
            "?limit=101",
            f"?q={'a' * 101}",
            # one below the smallest accepted values
            "?limit=0",
            "?offset=-1",
        ],
    )
    def test_rejects_bad_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(f"/api/mechanical-designers{query}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.usefixtures("designers")
class TestReadMechanicalDesigner:
    def test_returns_the_designer(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/mechanical-designers/kunio-okawara")

        assert response.status_code == status.HTTP_200_OK
        designer = response.json()["data"]
        assert designer["name_ja"] == "大河原邦男"
        assert "mobile_suits" not in designer

    def test_old_slug_returns_the_current_one(
        self, test_app_client: TestClient
    ) -> None:
        response = test_app_client.get("/api/mechanical-designers/okawara")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["slug"] == "kunio-okawara"

    def test_unknown_slug(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/mechanical-designers/yutaka-izubuchi")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Mechanical designer not found"}

    def test_malformed_slug(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/mechanical-designers/Kunio_Okawara")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.usefixtures("designers")
class TestReadMechanicalDesignerMobileSuits:
    def test_returns_their_suits_by_name(self, test_app_client: TestClient) -> None:
        response = test_app_client.get(
            "/api/mechanical-designers/okawara/mobile-suits?limit=1"
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        [item] = body["data"]
        assert item["mobile_suit"]["slug"] == "gundam"
        assert item["source"]["url"] == "https://gundam.fandom.com/?curid=1"
        assert body["meta"] == {"limit": 1, "offset": 0, "total": 2}

    def test_known_designer_with_no_suits(self, test_app_client: TestClient) -> None:
        response = test_app_client.get(
            "/api/mechanical-designers/hajime-katoki/mobile-suits"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []

    def test_unknown_designer(self, test_app_client: TestClient) -> None:
        response = test_app_client.get(
            "/api/mechanical-designers/yutaka-izubuchi/mobile-suits"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Mechanical designer not found"}

    @pytest.mark.parametrize(
        "path",
        [
            # one past the largest accepted value
            "kunio-okawara/mobile-suits?limit=101",
            # one below the smallest accepted values
            "kunio-okawara/mobile-suits?limit=0",
            "kunio-okawara/mobile-suits?offset=-1",
            # not a slug
            "Kunio_Okawara/mobile-suits",
        ],
    )
    def test_rejects_bad_parameters(
        self, test_app_client: TestClient, path: str
    ) -> None:
        response = test_app_client.get(f"/api/mechanical-designers/{path}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestUnexpectedErrors:
    @pytest.mark.parametrize(
        ("method", "path", "detail"),
        [
            ("get_page", "", "Error fetching mechanical designers"),
            ("get_one_by_slug", "/kunio-okawara", "Error fetching mechanical designer"),
            (
                "get_mobile_suit_page",
                "/kunio-okawara/mobile-suits",
                "Error fetching the designer's mobile suits",
            ),
        ],
    )
    def test_returns_a_fixed_500(
        self,
        test_app_client: TestClient,
        mocker: MockerFixture,
        method: str,
        path: str,
        detail: str,
    ) -> None:
        """FAPI-13: a fixed detail; the error text goes to the log."""
        mocker.patch.object(
            MechanicalDesignerFacade,
            method,
            autospec=True,
            side_effect=RuntimeError("connection reset"),
        )

        response = test_app_client.get(f"/api/mechanical-designers{path}")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": detail}
