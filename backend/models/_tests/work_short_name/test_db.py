import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.work.db import WorkDBFactory
from _factories.work_short_name.db import WorkShortNameDBFactory
from models._tests.integrity import violated_constraint
from models.work.db import WorkDB
from models.work_short_name.db import WorkShortNameDB

MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7001")
MSG_II_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7002")


@pytest.fixture
def msg_work_id(test_db_session: Session) -> uuid.UUID:
    WorkDBFactory(id=MSG_ID, title="Mobile Suit Gundam")
    test_db_session.commit()
    return MSG_ID


class TestWorkShortNameDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, msg_work_id: uuid.UUID, mock_utcnow: datetime
    ) -> None:
        WorkShortNameDBFactory(short_name="MSG", work_id=msg_work_id)
        test_db_session.commit()
        test_db_session.expunge_all()

        short_name = test_db_session.execute(
            select(WorkShortNameDB).where(WorkShortNameDB.short_name == "MSG")
        ).scalar_one()

        assert short_name.work_id == msg_work_id
        assert short_name.created_at == mock_utcnow

    def test_allows_several_short_names_for_one_work(
        self, test_db_session: Session, msg_work_id: uuid.UUID
    ) -> None:
        WorkShortNameDBFactory(short_name="MSG", work_id=msg_work_id)
        WorkShortNameDBFactory(short_name="MSG 0079", work_id=msg_work_id)

        test_db_session.flush()

    def test_deletes_short_names_with_their_work(
        self, test_db_session: Session, msg_work_id: uuid.UUID
    ) -> None:
        """ON DELETE CASCADE: a tag has no meaning without its work."""
        WorkShortNameDBFactory(short_name="MSG", work_id=msg_work_id)
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(WorkDB, msg_work_id))
        test_db_session.commit()

        assert test_db_session.scalars(select(WorkShortNameDB)).all() == []


class TestWorkShortNameDBConstraints:
    def test_rejects_a_short_name_used_by_another_work(
        self, test_db_session: Session, msg_work_id: uuid.UUID
    ) -> None:
        WorkDBFactory(id=MSG_II_ID, title="Mobile Suit Gundam II")
        WorkShortNameDBFactory(short_name="MSG", work_id=msg_work_id)
        WorkShortNameDBFactory(short_name="MSG", work_id=MSG_II_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "work_short_names_short_name_key",
        )

    @pytest.mark.parametrize(
        "short_name, constraint",
        [
            ("", "ck_work_short_names_short_name_not_empty"),
            (" MSG", "ck_work_short_names_short_name_trimmed"),
            ("MSG ", "ck_work_short_names_short_name_trimmed"),
        ],
    )
    def test_rejects_an_invalid_short_name(
        self,
        test_db_session: Session,
        msg_work_id: uuid.UUID,
        short_name: str,
        constraint: str,
    ) -> None:
        WorkShortNameDBFactory(short_name=short_name, work_id=msg_work_id)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)

    def test_rejects_a_missing_work(self, test_db_session: Session) -> None:
        WorkShortNameDBFactory(short_name="MSG", work_id=MSG_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "work_short_names_work_id_fkey",
        )
