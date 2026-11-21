import uuid
from datetime import date

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
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
from models.organization.facade import OrganizationFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8002")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8003")
EF_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8004")
WB_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8005")
GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8006")
GM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8007")


@pytest.fixture
def organizations(test_db_session: Session) -> None:
    """The Federation, one unit, and two suits it fields or develops."""
    ContinuityDBFactory(id=UC_ID, name="Universal Century", slug="universal-century")
    WorkDBFactory(
        id=MSG_ID,
        continuity_id=UC_ID,
        slug="mobile-suit-gundam",
        start_date=date(1979, 4, 7),
        title="Mobile Suit Gundam",
    )
    SourceDBFactory(id=SOURCE_ID, url="https://gundam.fandom.com/?curid=1")
    OrganizationDBFactory(id=EF_ID, name="Earth Federation", slug="earth-federation")
    OrganizationDBFactory(
        id=WB_ID,
        name="White Base Corps",
        parent_organization_id=EF_ID,
        slug="white-base-corps",
    )
    MobileSuitDBFactory(id=GUNDAM_ID, continuity_id=UC_ID, name="Gundam", slug="gundam")
    MobileSuitDBFactory(id=GM_ID, continuity_id=UC_ID, name="GM", slug="gm")
    # The links below have no ORM relationship to order them after their
    # rows, so the rows are flushed first.
    test_db_session.flush()
    OrganizationAppearanceDBFactory(
        organization_id=EF_ID, source_id=SOURCE_ID, work_id=MSG_ID
    )
    MobileSuitAppearanceDBFactory(
        mobile_suit_id=GUNDAM_ID, source_id=SOURCE_ID, work_id=MSG_ID
    )
    OrganizationSlugRedirectDBFactory(old_slug="efsf", organization_id=EF_ID)
    test_db_session.flush()
    for suit_id, role, work_id in (
        (GUNDAM_ID, MobileSuitOrganizationRole.OPERATOR, MSG_ID),
        (GUNDAM_ID, MobileSuitOrganizationRole.DEVELOPER, None),
        (GM_ID, MobileSuitOrganizationRole.OPERATOR, None),
    ):
        MobileSuitOrganizationDBFactory(
            mobile_suit_id=suit_id,
            organization_id=EF_ID,
            role=role,
            source_id=SOURCE_ID,
            work_id=work_id,
        )
    test_db_session.commit()


@pytest.mark.usefixtures("organizations")
class TestReadOrganizationsList:
    def test_returns_a_page(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/organizations")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert [o["slug"] for o in body["data"]] == [
            "earth-federation",
            "white-base-corps",
        ]
        assert body["data"][0]["parent_organization"] is None
        assert body["data"][1]["parent_organization"] == {
            "name": "Earth Federation",
            "slug": "earth-federation",
        }
        assert "id" not in body["data"][0]
        assert body["meta"] == {"limit": 50, "offset": 0, "total": 2}

    @pytest.mark.parametrize(
        ("query", "slugs", "total"),
        [
            ("?work=mobile-suit-gundam", ["earth-federation"], 1),
            ("?q=white base", ["white-base-corps"], 1),
            ("?offset=10", [], 2),
        ],
    )
    def test_filters_and_pages(
        self, test_app_client: TestClient, query: str, slugs: list[str], total: int
    ) -> None:
        response = test_app_client.get(f"/api/organizations{query}")

        assert response.status_code == status.HTTP_200_OK
        assert [o["slug"] for o in response.json()["data"]] == slugs
        assert response.json()["meta"]["total"] == total

    @pytest.mark.parametrize("query", ["?limit=0", "?offset=-1", f"?q={'a' * 101}"])
    def test_rejects_bad_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(f"/api/organizations{query}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            OrganizationFacade, "get_page", autospec=True, side_effect=RuntimeError
        )

        response = test_app_client.get("/api/organizations")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching organizations"}


@pytest.mark.usefixtures("organizations")
class TestReadOrganization:
    def test_returns_its_units_and_works(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/organizations/earth-federation")

        assert response.status_code == status.HTTP_200_OK
        federation = response.json()["data"]
        assert federation["child_organizations"] == [
            {"name": "White Base Corps", "slug": "white-base-corps"}
        ]
        assert [a["work"]["slug"] for a in federation["appearances"]] == [
            "mobile-suit-gundam"
        ]
        assert "mobile_suits" not in federation

    def test_old_slug_returns_the_current_one(
        self, test_app_client: TestClient
    ) -> None:
        response = test_app_client.get("/api/organizations/efsf")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["slug"] == "earth-federation"

    def test_unknown_slug(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/organizations/aeug")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Organization not found"}

    def test_malformed_slug(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/organizations/Earth_Federation")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            OrganizationFacade,
            "get_one_by_slug",
            autospec=True,
            side_effect=RuntimeError,
        )

        response = test_app_client.get("/api/organizations/earth-federation")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching organization"}


@pytest.mark.usefixtures("organizations")
class TestReadOrganizationMobileSuits:
    def test_returns_one_item_per_suit(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/organizations/efsf/mobile-suits")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert [
            (
                item["mobile_suit"]["slug"],
                [(link["role"], link["work"]) for link in item["links"]],
            )
            for item in body["data"]
        ] == [
            ("gm", [("operator", None)]),
            (
                "gundam",
                [
                    (
                        "operator",
                        {"slug": "mobile-suit-gundam", "title": "Mobile Suit Gundam"},
                    ),
                    ("developer", None),
                ],
            ),
        ]
        assert body["meta"] == {"limit": 50, "offset": 0, "total": 2}

    def test_filters_by_role(self, test_app_client: TestClient) -> None:
        response = test_app_client.get(
            "/api/organizations/earth-federation/mobile-suits?role=developer"
        )

        assert response.status_code == status.HTTP_200_OK
        [item] = response.json()["data"]
        assert item["mobile_suit"]["slug"] == "gundam"
        assert [link["role"] for link in item["links"]] == ["developer"]
        assert response.json()["meta"]["total"] == 1

    def test_known_organization_with_no_suits(
        self, test_app_client: TestClient
    ) -> None:
        response = test_app_client.get(
            "/api/organizations/white-base-corps/mobile-suits"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []

    def test_unknown_organization(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/organizations/aeug/mobile-suits")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Organization not found"}

    @pytest.mark.parametrize("query", ["?role=pilot", "?limit=101", "?offset=-1"])
    def test_rejects_bad_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(
            f"/api/organizations/earth-federation/mobile-suits{query}"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            OrganizationFacade,
            "get_mobile_suit_page",
            autospec=True,
            side_effect=RuntimeError,
        )

        response = test_app_client.get(
            "/api/organizations/earth-federation/mobile-suits"
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {
            "detail": "Error fetching the organization's mobile suits"
        }
