from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from _factories.ingest_run.db import IngestRunDBFactory
from config.env_vars import EnvVarManager
from constants.catalog import IngestRunStatus
from models.mobile_suit.db import MobileSuitDB
from models.source.db import SourceDB
from models.spec_sheet.db import SpecSheetDB
from models.work.db import WorkDB
from scripts.seed_dev import SeedRefusedError, fandom_url, main, run


@pytest.fixture
def prod_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("ENVIRONMENT", "prod")
    EnvVarManager().reload()
    yield
    monkeypatch.undo()
    EnvVarManager().reload()


def updated_ats(db_session: Session) -> dict[str, datetime]:
    stamps: dict[str, datetime] = {}
    for model in (SourceDB, WorkDB, MobileSuitDB, SpecSheetDB):
        for row in db_session.scalars(select(model)):
            stamps[f"{model.__name__}:{row.id}"] = row.updated_at
    return stamps


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

    def test_rerun_changes_nothing(self, test_db_session: Session) -> None:
        run(test_db_session, force=False)
        before = updated_ats(test_db_session)

        run(test_db_session, force=False)

        assert updated_ats(test_db_session) == before

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
