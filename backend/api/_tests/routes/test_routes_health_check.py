from fastapi import status
from fastapi.testclient import TestClient


class TestReadHealthCheck:
    def test_reports_ok(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/health-check")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"data": {"status": "ok"}}

    def test_rejects_other_methods(self, test_app_client: TestClient) -> None:
        response = test_app_client.post("/api/health-check")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
