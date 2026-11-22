from collections.abc import Iterator
from datetime import datetime
from typing import Any

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from _factories.ingest_run.db import IngestRunDBFactory
from config.env_vars import EnvVarManager
from constants.catalog import IngestRunStatus
from db.base_db import RootDB
from models.mobile_suit.db import MobileSuitDB
from scripts.seed_dev import SeedRefusedError, fandom_url, main, run


@pytest.fixture
def prod_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("ENVIRONMENT", "prod")
    EnvVarManager().reload()
    yield
    monkeypatch.undo()
    EnvVarManager().reload()


def snapshot(db_session: Session) -> dict[tuple[str, tuple[object, ...]], datetime]:
    """Every row of every table, by primary key, with its last write.

    ``updated_at`` where the table has one, else ``created_at``: a link
    rewritten by delete and insert gets a new one, and a duplicate adds
    a key.
    """
    rows: dict[tuple[str, tuple[object, ...]], datetime] = {}
    for mapper in RootDB.registry.mappers:
        model = mapper.class_
        stamp = "updated_at" if hasattr(model, "updated_at") else "created_at"
        for row in db_session.scalars(select(model)):
            identity = inspect(row).identity
            assert identity is not None
            rows[(model.__tablename__, identity)] = getattr(row, stamp)
    return rows


class TestRun:
    def test_seeds_every_route(
        self, test_db_session: Session, test_app_client: TestClient
    ) -> None:
        run(test_db_session, force=False)

        continuities = test_app_client.get("/api/continuities").json()["data"]
        works = test_app_client.get("/api/works").json()
        suits = test_app_client.get("/api/mobile-suits?q=rx78").json()
        work_suits = test_app_client.get("/api/works/mobile-suit-gundam/mobile-suits")
        gundam = test_app_client.get("/api/mobile-suits/rx-78-2").json()["data"]
        work = test_app_client.get("/api/works/mobile-suit-gundam-i").json()["data"]
        renamed_work = test_app_client.get("/api/works/msg").json()["data"]

        assert [c["slug"] for c in continuities] == ["universal-century"]
        assert works["meta"]["total"] == 5
        assert [s["slug"] for s in suits["data"]] == [
            "rx-78-2-gundam",
            "rx-78-02-gundam",
            "rx-78f00-gundam",
        ]
        assert work_suits.status_code == status.HTTP_200_OK
        assert [(s["slug"], s["is_debut"]) for s in work_suits.json()["data"]] == [
            ("rx-78-2-gundam", True),
            ("ms-06f-zaku-ii", True),
        ]
        assert gundam["slug"] == "rx-78-2-gundam"
        assert renamed_work["slug"] == "mobile-suit-gundam"
        base, magnet_coating = gundam["spec_sheets"]
        assert (base["configuration"], base["turn_time_s"]) == (None, 1.5)
        assert magnet_coating["configuration"] == "Magnet Coating"
        assert magnet_coating["turn_time_s"] == 1.1
        assert magnet_coating["head_height_m"] == 18.0
        # Every base value but the turn time, which this sheet states.
        assert magnet_coating["inherited_fields"] == [
            "empty_weight_kg",
            "generator_output_kw",
            "gross_weight_kg",
            "head_height_m",
            "max_acceleration_g",
            "max_speed_kmh",
            "sensor_range_m",
            "total_thrust_kg",
        ]
        assert [r["mobile_suit"]["slug"] for r in gundam["relations"]] == [
            "rx-78-02-gundam",
            "rx-78f00-gundam",
        ]
        assert gundam["appearances"][0]["source"]["revision_url"] == (
            "https://gundam.fandom.com/wiki/RX-78-2_Gundam?oldid=707889"
        )
        assert [(r["relation_type"], r["work"]["slug"]) for r in work["relations"]] == [
            ("compilation_of", "mobile-suit-gundam")
        ]

    def test_seeds_every_people_route(
        self, test_db_session: Session, test_app_client: TestClient
    ) -> None:
        """Old slugs resolve, and each page lists what its infobox does.

        Okawara is credited with three of the four suits; the Origin's
        Amuro pilots with no work, as his suit's infobox gives none.
        """
        run(test_db_session, force=False)

        def get(path: str) -> dict[str, Any]:
            response = test_app_client.get(path)
            assert response.status_code == status.HTTP_200_OK, path
            return response.json()

        characters = get("/api/characters?q=amuro")
        amuro = get("/api/characters/amuro")["data"]
        organizations = get("/api/organizations?work=mobile-suit-gundam")
        federation = get("/api/organizations/earth-federation-universal-century")
        zeon_suits = get("/api/organizations/principality-of-zeon/mobile-suits")
        designers = get("/api/mechanical-designers")
        katoki = get("/api/mechanical-designers/katoki-hajime")["data"]
        okawara_suits = get("/api/mechanical-designers/kunio-okawara/mobile-suits")
        origin_gundam = get("/api/mobile-suits/rx-78-02-gundam")["data"]
        rx_78_2_gundam = get("/api/mobile-suits/rx-78-2-gundam")["data"]

        assert [c["slug"] for c in characters["data"]] == [
            "amuro-ray",
            "amuro-ray-origin",
        ]
        assert amuro["slug"] == "amuro-ray"
        assert [a["work"]["slug"] for a in amuro["appearances"]] == [
            "mobile-suit-gundam",
            "mobile-suit-gundam-i",
        ]
        assert [
            (p["mobile_suit"]["slug"], p["work"]["slug"])
            for p in amuro["piloted_mobile_suits"]
        ] == [("rx-78-2-gundam", "mobile-suit-gundam")]
        assert amuro["appearances"][0]["source"]["url"] == (
            "https://gundam.fandom.com/wiki/Amuro_Ray"
        )
        assert [o["slug"] for o in organizations["data"]] == [
            "earth-federation",
            "principality-of-zeon",
        ]
        assert federation["data"]["slug"] == "earth-federation"
        assert [
            (item["mobile_suit"]["slug"], [link["role"] for link in item["links"]])
            for item in zeon_suits["data"]
        ] == [("ms-06f-zaku-ii", ["operator"])]
        assert [d["slug"] for d in designers["data"]] == [
            "hajime-katoki",
            "kunio-okawara",
            "masaki-kawahara",
        ]
        assert katoki["slug"] == "hajime-katoki"
        assert okawara_suits["meta"]["total"] == 3
        assert [
            d["mechanical_designer"]["slug"] for d in origin_gundam["designers"]
        ] == [
            "hajime-katoki",
            "kunio-okawara",
        ]
        assert [
            (p["character"]["slug"], p["work"]) for p in origin_gundam["pilots"]
        ] == [("amuro-ray-origin", None)]
        assert [
            (o["organization"]["slug"], o["role"])
            for o in rx_78_2_gundam["organizations"]
        ] == [("earth-federation", "manufacturer")]
        assert rx_78_2_gundam["pilots"][0]["source"]["url"] == (
            "https://gundam.fandom.com/wiki/RX-78-2_Gundam"
        )

    def test_rerun_changes_nothing(self, test_db_session: Session) -> None:
        """No table gains, loses or rewrites a row, links included."""
        run(test_db_session, force=False)
        before = snapshot(test_db_session)

        run(test_db_session, force=False)
        after = snapshot(test_db_session)

        assert after.keys() == before.keys()
        assert after == before
        assert {table for table, _ in before} >= {
            "character_slug_redirects",
            "mobile_suit_designers",
            "mobile_suit_organizations",
            "mobile_suit_pilots",
            "organization_appearances",
        }

    def test_refuses_after_a_completed_ingest_run(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        IngestRunDBFactory(
            finished_at=mock_utcnow,
            status=IngestRunStatus.SUCCEEDED,
        )
        test_db_session.commit()

        with pytest.raises(SeedRefusedError, match="--force"):
            run(test_db_session, force=False)

        assert test_db_session.scalars(select(MobileSuitDB)).all() == []

    def test_runs_after_a_failed_ingest_run(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        IngestRunDBFactory(
            finished_at=mock_utcnow,
            status=IngestRunStatus.FAILED,
        )
        test_db_session.commit()

        run(test_db_session, force=False)

        assert len(test_db_session.scalars(select(MobileSuitDB)).all()) == 4

    def test_force_seeds_after_a_completed_ingest_run(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        IngestRunDBFactory(
            finished_at=mock_utcnow,
            status=IngestRunStatus.SUCCEEDED,
        )
        test_db_session.commit()

        run(test_db_session, force=True)

        assert len(test_db_session.scalars(select(MobileSuitDB)).all()) == 4

    @pytest.mark.usefixtures("prod_environment")
    def test_refuses_outside_dev_and_test(self, test_db_session: Session) -> None:
        with pytest.raises(SeedRefusedError, match="'prod'"):
            run(test_db_session, force=True)


class TestMain:
    @pytest.mark.usefixtures("prod_environment")
    def test_exits_1_outside_dev_and_test(self) -> None:
        assert main(["--force"]) == 1


class TestFandomUrl:
    @pytest.mark.parametrize(
        ("title", "url"),
        [
            ("RX-78-2 Gundam", "https://gundam.fandom.com/wiki/RX-78-2_Gundam"),
            (
                "Mobile Suit Gundam: The Origin",
                "https://gundam.fandom.com/wiki/Mobile_Suit_Gundam:_The_Origin",
            ),
            (
                "It Moves? Gundam, Follow Your Dreams!",
                "https://gundam.fandom.com/wiki/It_Moves%3F_Gundam,_Follow_Your_Dreams!",
            ),
        ],
    )
    def test_builds_the_article_url(self, title: str, url: str) -> None:
        assert fandom_url(title) == url
