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
from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from _factories.work_relation.db import WorkRelationDBFactory
from _factories.work_slug_redirect.db import WorkSlugRedirectDBFactory
from constants.catalog import WorkRelationType, WorkType
from models.mobile_suit.facade import MobileSuitFacade
from models.work.facade import WorkFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba002")
MOVIE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba003")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba004")


@pytest.fixture
def works(test_db_session: Session) -> None:
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
    # The edges below have no ORM relationship to order them after their
    # works, so the works are flushed first.
    test_db_session.flush()
    SourceDBFactory(
        id=SOURCE_ID, revision_id=706484, url="https://gundam.fandom.com/?curid=1"
    )
    WorkRelationDBFactory(
        from_work_id=MOVIE_ID,
        relation_type=WorkRelationType.COMPILATION_OF,
        source_id=SOURCE_ID,
        to_work_id=MSG_ID,
    )
    WorkSlugRedirectDBFactory(old_slug="gundam-0079", work_id=MSG_ID)
    test_db_session.commit()


@pytest.mark.usefixtures("works")
class TestReadWorksList:
    def test_returns_a_page(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/works")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert [work["slug"] for work in body["data"]] == [
            "mobile-suit-gundam",
            "mobile-suit-gundam-i",
        ]
        assert body["data"][0]["continuity"] == {
            "name": "Universal Century",
            "slug": "universal-century",
        }
        assert "id" not in body["data"][0]
        assert body["meta"] == {"limit": 50, "offset": 0, "total": 2}

    @pytest.mark.parametrize(
        ("query", "slugs", "total"),
        [
            ("?work_type=film", ["mobile-suit-gundam-i"], 1),
            (
                "?continuity=universal-century&work_type=tv_series",
                ["mobile-suit-gundam"],
                1,
            ),
            ("?continuity=cosmic-era", [], 0),
            ("?limit=1&offset=1", ["mobile-suit-gundam-i"], 2),
            ("?offset=10", [], 2),
        ],
    )
    def test_filters_and_pages(
        self, test_app_client: TestClient, query: str, slugs: list[str], total: int
    ) -> None:
        response = test_app_client.get(f"/api/works{query}")

        assert response.status_code == status.HTTP_200_OK
        assert [work["slug"] for work in response.json()["data"]] == slugs
        assert response.json()["meta"]["total"] == total

    @pytest.mark.parametrize(
        "query", ["?limit=0", "?limit=101", "?offset=-1", "?work_type=anime"]
    )
    def test_rejects_bad_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(f"/api/works{query}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestReadWorksListEmpty:
    def test_empty_database(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/works")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [],
            "meta": {"limit": 50, "offset": 0, "total": 0},
        }

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            WorkFacade, "get_page", autospec=True, side_effect=RuntimeError
        )

        response = test_app_client.get("/api/works")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching works"}


@pytest.mark.usefixtures("works")
class TestReadWork:
    def test_returns_the_work_with_parent_and_relations(
        self, test_app_client: TestClient
    ) -> None:
        response = test_app_client.get("/api/works/mobile-suit-gundam-i")

        assert response.status_code == status.HTTP_200_OK
        work = response.json()["data"]
        assert work["parent_work"] == {
            "slug": "mobile-suit-gundam",
            "title": "Mobile Suit Gundam",
        }
        [relation] = work["relations"]
        assert relation["direction"] == "outgoing"
        assert relation["relation_type"] == "compilation_of"
        assert relation["work"]["slug"] == "mobile-suit-gundam"
        assert relation["source"] == {
            "content_license": "cc_by_sa_3_0",
            "kind": "fandom_page",
            "license_name": "CC BY-SA 3.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/3.0/",
            "retrieved_at": relation["source"]["retrieved_at"],
            "revision_id": 706484,
            "revision_url": "https://gundam.fandom.com/?curid=1&oldid=706484",
            "url": "https://gundam.fandom.com/?curid=1",
        }

    def test_old_slug_returns_the_current_one(
        self, test_app_client: TestClient
    ) -> None:
        response = test_app_client.get("/api/works/gundam-0079")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["slug"] == "mobile-suit-gundam"

    def test_unknown_slug(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/works/turn-a-gundam")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Work not found"}

    @pytest.mark.parametrize("slug", ["Mobile-Suit-Gundam", "gundam_0079", "-gundam"])
    def test_malformed_slug(self, test_app_client: TestClient, slug: str) -> None:
        response = test_app_client.get(f"/api/works/{slug}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            WorkFacade, "get_one_by_slug", autospec=True, side_effect=RuntimeError
        )

        response = test_app_client.get("/api/works/mobile-suit-gundam")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching work"}


@pytest.mark.usefixtures("works")
class TestReadWorkMobileSuits:
    def test_returns_the_suits_debuts_first(
        self, test_app_client: TestClient, test_db_session: Session
    ) -> None:
        for name, is_debut in (("Acguy", False), ("Gundam", True)):
            suit = MobileSuitDBFactory(name=name)
            MobileSuitAppearanceDBFactory(
                first_episode=1,
                is_debut=is_debut,
                last_episode=43,
                mobile_suit_id=suit.id,
                source_id=SOURCE_ID,
                work_id=MSG_ID,
            )
        test_db_session.commit()

        response = test_app_client.get("/api/works/gundam-0079/mobile-suits?limit=1")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert [
            (s["name"], s["is_debut"], s["last_episode"]) for s in body["data"]
        ] == [("Gundam", True, 43)]
        assert body["meta"] == {"limit": 1, "offset": 0, "total": 2}

    def test_known_work_with_no_suits(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/works/mobile-suit-gundam-i/mobile-suits")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"] == []

    def test_unknown_work(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/works/turn-a-gundam/mobile-suits")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Work not found"}

    @pytest.mark.parametrize("query", ["?limit=0", "?limit=101", "?offset=-1"])
    def test_rejects_bad_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(
            f"/api/works/mobile-suit-gundam/mobile-suits{query}"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            MobileSuitFacade,
            "get_page_by_work_slug",
            autospec=True,
            side_effect=RuntimeError,
        )

        response = test_app_client.get("/api/works/mobile-suit-gundam/mobile-suits")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching the work's mobile suits"}
