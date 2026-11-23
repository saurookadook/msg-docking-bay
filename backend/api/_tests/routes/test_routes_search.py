import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from _factories.character.db import CharacterDBFactory
from _factories.continuity.db import ContinuityDBFactory
from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.organization.db import OrganizationDBFactory
from _factories.work.db import WorkDBFactory
from models.search.facade import CatalogSearchFacade


@pytest.fixture
def catalog(test_db_session: Session) -> None:
    """One or two rows of every kind."""
    uc = ContinuityDBFactory(name="Universal Century", slug="universal-century")
    test_db_session.flush()
    MobileSuitDBFactory(
        continuity_id=uc.id,
        model_number="RX-78-2",
        name="Gundam",
        slug="rx-78-2-gundam",
    )
    MobileSuitDBFactory(model_number="MS-06F", name="Zaku II", slug="zaku-ii")
    CharacterDBFactory(name="Amuro Ray", name_ja="アムロ・レイ", slug="amuro-ray")
    OrganizationDBFactory(name="Principality of Zeon", slug="principality-of-zeon")
    OrganizationDBFactory(name="Zeonic", slug="zeonic")
    MechanicalDesignerDBFactory(name="Kunio Okawara", slug="kunio-okawara")
    WorkDBFactory(slug="mobile-suit-gundam", title="Mobile Suit Gundam")
    test_db_session.commit()


def slugs(
    body: dict[str, dict[str, list[dict[str, object]]]],
) -> dict[str, list[object]]:
    return {
        kind: [card["slug"] for card in cards] for kind, cards in body["data"].items()
    }


@pytest.mark.usefixtures("catalog")
class TestReadSearch:
    def test_returns_each_kinds_matches_and_totals(
        self, test_app_client: TestClient
    ) -> None:
        response = test_app_client.get("/api/search?q=gundam")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert slugs(body) == {
            "characters": [],
            "mechanical_designers": [],
            "mobile_suits": ["rx-78-2-gundam"],
            "organizations": [],
            "works": ["mobile-suit-gundam"],
        }
        [suit] = body["data"]["mobile_suits"]
        assert suit["model_number"] == "RX-78-2"
        assert suit["continuity"] == {
            "name": "Universal Century",
            "slug": "universal-century",
        }
        assert "id" not in suit
        assert body["meta"] == {
            "limit": 5,
            "totals": {
                "characters": 0,
                "mechanical_designers": 0,
                "mobile_suits": 1,
                "organizations": 0,
                "works": 1,
            },
        }

    def test_limits_each_kind(self, test_app_client: TestClient) -> None:
        """``zeon`` matches two organizations; one is shown (Q1, Q3)."""
        response = test_app_client.get("/api/search?q=zeon&limit=1")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert slugs(body)["organizations"] == ["zeonic"]
        assert body["meta"]["limit"] == 1
        assert body["meta"]["totals"]["organizations"] == 2

    @pytest.mark.parametrize("query", ["", "?q=", "?q=%20--%20", "?q=大河原"])
    def test_blank_q_lists_the_first_rows(
        self, test_app_client: TestClient, query: str
    ) -> None:
        """A missing or blank ``q`` is no filter (Q4, Q5); Japanese is
        blank after normalization, until #34.
        """
        response = test_app_client.get(f"/api/search{query}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["meta"]["totals"] == {
            "characters": 1,
            "mechanical_designers": 1,
            "mobile_suits": 2,
            "organizations": 2,
            "works": 1,
        }

    @pytest.mark.parametrize(
        "query",
        [
            # the largest accepted values
            "?limit=20",
            f"?q={'a' * 100}",
            # the smallest accepted value
            "?limit=1",
        ],
    )
    def test_accepts_boundary_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(f"/api/search{query}")

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "query",
        [
            # one past the largest accepted values
            "?limit=21",
            f"?q={'a' * 101}",
            # one below the smallest accepted value
            "?limit=0",
            "?limit=five",
        ],
    )
    def test_rejects_bad_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(f"/api/search{query}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestReadSearchEmpty:
    def test_empty_database(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/search?q=gundam")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert all(cards == [] for cards in body["data"].values())
        assert set(body["meta"]["totals"].values()) == {0}

    def test_returns_a_fixed_500(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        """FAPI-13: a fixed detail; the error text goes to the log."""
        mocker.patch.object(
            CatalogSearchFacade,
            "search",
            autospec=True,
            side_effect=RuntimeError("reset"),
        )

        response = test_app_client.get("/api/search?q=gundam")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error searching the catalog"}
