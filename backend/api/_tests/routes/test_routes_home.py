from fastapi import status
from fastapi.testclient import TestClient


class TestReadHome:
    def test_returns_the_static_welcome(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == {
            "message": "Welcome to the msg-docking-bay API.",
            "name": "msg-docking-bay",
        }

    def test_responds_with_json(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api")

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/json"
