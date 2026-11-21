import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_appearance.db import MobileSuitAppearanceDBFactory
from _factories.mobile_suit_relation.db import MobileSuitRelationDBFactory
from _factories.mobile_suit_slug_redirect.db import MobileSuitSlugRedirectDBFactory
from _factories.source.db import SourceDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.work.db import WorkDBFactory
from constants.catalog import MobileSuitRelationType, UnitType
from models.mobile_suit.facade import MobileSuitFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc002")
GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc003")
ZAKU_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc004")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc005")


@pytest.fixture
def suits(test_db_session: Session) -> None:
    ContinuityDBFactory(id=UC_ID, name="Universal Century", slug="universal-century")
    WorkDBFactory(id=MSG_ID, continuity_id=UC_ID, slug="mobile-suit-gundam")
    MobileSuitDBFactory(
        id=GUNDAM_ID,
        continuity_id=UC_ID,
        model_number="RX-78-2",
        name="Gundam",
        slug="rx-78-2-gundam",
    )
    MobileSuitDBFactory(
        id=ZAKU_ID,
        continuity_id=UC_ID,
        model_number="MS-06F",
        name="Zaku II",
        slug="zaku-ii",
    )
    MobileSuitDBFactory(name="Ball", slug="ball", unit_type=UnitType.POD)
    SourceDBFactory(id=SOURCE_ID, url="https://gundam.fandom.com/?curid=2034")
    # The rows below have no ORM relationship to order them after their
    # suits, so the suits are flushed first.
    test_db_session.flush()
    MobileSuitAppearanceDBFactory(
        is_debut=True, mobile_suit_id=GUNDAM_ID, source_id=SOURCE_ID, work_id=MSG_ID
    )
    SpecSheetDBFactory(
        head_height_m=18.0,
        mobile_suit_id=GUNDAM_ID,
        raw_infobox={"height": "18.0 meters"},
        source_id=SOURCE_ID,
    )
    SpecSheetDBFactory(
        configuration="G-Armor",
        gross_weight_kg=80000.0,
        mobile_suit_id=GUNDAM_ID,
        source_id=SOURCE_ID,
    )
    MobileSuitRelationDBFactory(
        from_mobile_suit_id=GUNDAM_ID,
        relation_type=MobileSuitRelationType.DEVELOPED_FROM,
        source_id=SOURCE_ID,
        to_mobile_suit_id=ZAKU_ID,
    )
    MobileSuitSlugRedirectDBFactory(mobile_suit_id=GUNDAM_ID, old_slug="gundam")
    test_db_session.commit()


@pytest.mark.usefixtures("suits")
class TestReadMobileSuitsList:
    def test_returns_a_page_by_name(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/mobile-suits")

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert [suit["slug"] for suit in body["data"]] == [
            "ball",
            "rx-78-2-gundam",
            "zaku-ii",
        ]
        assert set(body["data"][1]) == {
            "continuity",
            "created_at",
            "model_number",
            "name",
            "name_ja",
            "slug",
            "unit_type",
            "updated_at",
        }
        assert body["meta"] == {"limit": 50, "offset": 0, "total": 3}

    @pytest.mark.parametrize(
        ("query", "slugs", "total"),
        [
            ("?q=rx782", ["rx-78-2-gundam"], 1),
            ("?q=%20", ["ball", "rx-78-2-gundam", "zaku-ii"], 3),
            ("?unit_type=pod", ["ball"], 1),
            ("?continuity=universal-century", ["rx-78-2-gundam", "zaku-ii"], 2),
            ("?work=mobile-suit-gundam", ["rx-78-2-gundam"], 1),
            ("?work=mobile-suit-gundam&q=zaku", [], 0),
            ("?limit=1&offset=2", ["zaku-ii"], 3),
            ("?offset=3", [], 3),
        ],
    )
    def test_filters_and_pages(
        self, test_app_client: TestClient, query: str, slugs: list[str], total: int
    ) -> None:
        response = test_app_client.get(f"/api/mobile-suits{query}")

        assert response.status_code == status.HTTP_200_OK
        assert [suit["slug"] for suit in response.json()["data"]] == slugs
        assert response.json()["meta"]["total"] == total

    @pytest.mark.parametrize(
        "query",
        ["?limit=0", "?limit=101", "?offset=-1", "?unit_type=robot", f"?q={'a' * 101}"],
    )
    def test_rejects_bad_parameters(
        self, test_app_client: TestClient, query: str
    ) -> None:
        response = test_app_client.get(f"/api/mobile-suits{query}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestReadMobileSuitsListEmpty:
    def test_empty_database(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/mobile-suits")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "data": [],
            "meta": {"limit": 50, "offset": 0, "total": 0},
        }

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            MobileSuitFacade, "get_page", autospec=True, side_effect=RuntimeError
        )

        response = test_app_client.get("/api/mobile-suits")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching mobile suits"}


@pytest.mark.usefixtures("suits")
class TestReadMobileSuit:
    def test_returns_the_suit_with_its_lists(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/mobile-suits/rx-78-2-gundam")

        assert response.status_code == status.HTTP_200_OK
        suit = response.json()["data"]
        assert suit["model_number"] == "RX-78-2"
        assert [
            (
                s["configuration"],
                s["head_height_m"],
                s["gross_weight_kg"],
                s["inherited_fields"],
            )
            for s in suit["spec_sheets"]
        ] == [(None, 18.0, None, []), ("G-Armor", 18.0, 80000.0, ["head_height_m"])]
        assert "raw_infobox" not in suit["spec_sheets"][0]
        assert [
            (r["direction"], r["mobile_suit"]["slug"]) for r in suit["relations"]
        ] == [("outgoing", "zaku-ii")]
        assert [(a["work"]["slug"], a["is_debut"]) for a in suit["appearances"]] == [
            ("mobile-suit-gundam", True)
        ]
        assert suit["appearances"][0]["source"]["revision_url"] is None
        # Empty here; the facade tests cover their contents.
        assert (suit["pilots"], suit["organizations"], suit["designers"]) == (
            [],
            [],
            [],
        )

    def test_old_slug_returns_the_current_one(
        self, test_app_client: TestClient
    ) -> None:
        response = test_app_client.get("/api/mobile-suits/gundam")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["slug"] == "rx-78-2-gundam"

    def test_unknown_slug(self, test_app_client: TestClient) -> None:
        response = test_app_client.get("/api/mobile-suits/gp01")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Mobile suit not found"}

    @pytest.mark.parametrize("slug", ["RX-78-2", "rx_78_2", "rx--78"])
    def test_malformed_slug(self, test_app_client: TestClient, slug: str) -> None:
        response = test_app_client.get(f"/api/mobile-suits/{slug}")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unexpected_error(
        self, test_app_client: TestClient, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            MobileSuitFacade, "get_one_by_slug", autospec=True, side_effect=RuntimeError
        )

        response = test_app_client.get("/api/mobile-suits/rx-78-2-gundam")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Error fetching mobile suit"}
