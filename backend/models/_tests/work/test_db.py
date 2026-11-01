import uuid
from datetime import date, datetime
from typing import Any

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from _factories.work.db import WorkDBFactory
from constants.catalog import WorkType
from models._tests.integrity import violated_constraint
from models.work.db import WorkDB

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b5ada")
WFM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b6001")
WFM_SEASON_1_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b6002")


class TestWorkDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        ContinuityDBFactory(id=UC_ID)
        WorkDBFactory(
            id=WFM_ID,
            anilist_id=139274,
            ann_id=24735,
            continuity_id=UC_ID,
            end_date=date(2023, 7, 2),
            fandom_page_title="Mobile Suit Gundam: The Witch from Mercury",
            slug="the-witch-from-mercury",
            start_date=date(2022, 10, 2),
            title="Mobile Suit Gundam: The Witch from Mercury",
            title_ja="機動戦士ガンダム 水星の魔女",
            wikidata_qid="Q111111111",
            work_type=WorkType.TV_SERIES,
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        work = test_db_session.execute(
            select(WorkDB).where(WorkDB.id == WFM_ID)
        ).scalar_one()

        assert work.anilist_id == 139274
        assert work.ann_id == 24735
        assert work.continuity_id == UC_ID
        assert work.end_date == date(2023, 7, 2)
        assert work.fandom_page_title == "Mobile Suit Gundam: The Witch from Mercury"
        assert work.slug == "the-witch-from-mercury"
        assert work.start_date == date(2022, 10, 2)
        assert work.title == "Mobile Suit Gundam: The Witch from Mercury"
        assert work.title_ja == "機動戦士ガンダム 水星の魔女"
        assert work.wikidata_qid == "Q111111111"
        assert work.work_type is WorkType.TV_SERIES
        assert work.created_at == mock_utcnow

    def test_stores_the_work_type_value_not_the_member_name(
        self, test_db_session: Session
    ) -> None:
        """SQLAlchemy stores enum names by default (SQLA-11)."""
        WorkDBFactory(id=WFM_ID, work_type=WorkType.VIDEO_GAME)
        test_db_session.commit()

        stored = test_db_session.execute(
            text("SELECT work_type::text FROM works WHERE id = :id"), {"id": WFM_ID}
        ).scalar_one()

        assert stored == "video_game"

    def test_clears_the_parent_link_when_the_series_is_deleted(
        self, test_db_session: Session
    ) -> None:
        series = WorkDBFactory(id=WFM_ID)
        WorkDBFactory(id=WFM_SEASON_1_ID, parent_work_id=WFM_ID)
        test_db_session.commit()

        test_db_session.delete(series)
        test_db_session.commit()
        test_db_session.expunge_all()

        season = test_db_session.get_one(WorkDB, WFM_SEASON_1_ID)
        assert season.parent_work_id is None

    def test_clears_the_continuity_when_the_continuity_is_deleted(
        self, test_db_session: Session
    ) -> None:
        uc = ContinuityDBFactory(id=UC_ID)
        WorkDBFactory(id=WFM_ID, continuity_id=UC_ID)
        test_db_session.commit()

        test_db_session.delete(uc)
        test_db_session.commit()
        test_db_session.expunge_all()

        assert test_db_session.get_one(WorkDB, WFM_ID).continuity_id is None

    def test_allows_two_works_with_the_same_title(
        self, test_db_session: Session
    ) -> None:
        WorkDBFactory(title="Mobile Suit Gundam", work_type=WorkType.TV_SERIES)
        WorkDBFactory(title="Mobile Suit Gundam", work_type=WorkType.VIDEO_GAME)

        test_db_session.flush()


class TestWorkDBConstraints:
    @pytest.mark.parametrize(
        "column, value, constraint",
        [
            ("anilist_id", 80, "works_anilist_id_key"),
            ("ann_id", 1270, "works_ann_id_key"),
            ("fandom_page_title", "Mobile Suit Gundam", "works_fandom_page_title_key"),
            ("slug", "mobile-suit-gundam", "works_slug_key"),
            ("wikidata_qid", "Q1134906", "works_wikidata_qid_key"),
        ],
    )
    def test_rejects_a_duplicate(
        self, test_db_session: Session, column: str, value: int | str, constraint: str
    ) -> None:
        WorkDBFactory(**{column: value})
        WorkDBFactory(**{column: value})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23505", constraint)

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"anilist_id": 0}, "ck_works_anilist_id_positive"),
            ({"ann_id": -1}, "ck_works_ann_id_positive"),
            (
                {"start_date": date(2022, 10, 2), "end_date": date(2022, 10, 1)},
                "ck_works_end_after_start",
            ),
            ({"fandom_page_title": ""}, "ck_works_fandom_page_title_not_empty"),
            ({"slug": "Mobile_Suit_Gundam"}, "ck_works_slug_format"),
            ({"title": ""}, "ck_works_title_not_empty"),
            ({"title_ja": ""}, "ck_works_title_ja_not_empty"),
            ({"wikidata_qid": "1134906"}, "ck_works_wikidata_qid_format"),
            ({"wikidata_qid": "Q"}, "ck_works_wikidata_qid_format"),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        WorkDBFactory(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)

    def test_rejects_a_work_that_is_its_own_parent(
        self, test_db_session: Session
    ) -> None:
        WorkDBFactory(id=WFM_ID, parent_work_id=WFM_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_works_not_own_parent",
        )

    def test_accepts_open_ended_dates(self, test_db_session: Session) -> None:
        """A NULL date passes the CHECK: a running series has no end."""
        WorkDBFactory(start_date=date(2025, 4, 9), end_date=None)

        test_db_session.flush()
