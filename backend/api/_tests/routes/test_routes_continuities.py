from datetime import datetime

from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from models.continuity.facade import ContinuityFacade


class TestReadContinuitiesList:
    def test_returns_every_continuity_by_name(
        self,
        test_app_client: TestClient,
        test_db_session: Session,
        mock_utcnow: datetime,
    ) -> None:
        uc = ContinuityDBFactory(name="Universal Century", slug="universal-century")
        ContinuityDBFactory(
            name="Universal Century (GQ)",
            parent_continuity_id=uc.id,
            slug="universal-century-gq",
        )
        test_db_session.commit()

        response = test_app_client.get("/api/continuities")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [
                {
                    "created_at": mock_utcnow.isoformat().replace("+00:00", "Z"),
                    "name": "Universal Century",
                    "parent_continuity": None,
                    "slug": "universal-century",
                    "updated_at": mock_utcnow.isoformat().replace("+00:00", "Z"),
                },
                {
                    "created_at": mock_utcnow.isoformat().replace("+00:00", "Z"),
                    "name": "Universal Century (GQ)",
                    "parent_continuity": {
                        "name": "Universal Century",
                        "slug": "universal-century",
                    },
                    "slug": "universal-century-gq",
                    "updated_at": mock_utcnow.isoformat().replace("+00:00", "Z"),
                },
            ]
        }

    def test_empty_database(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/continuities")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"data": []}

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            ContinuityFacade, "get_all", autospec=True, side_effect=RuntimeError
        )

        response = test_app_client.get("/api/continuities")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching continuities"}
