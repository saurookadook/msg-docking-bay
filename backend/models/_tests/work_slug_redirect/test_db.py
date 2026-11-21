import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.work.db import WorkDBFactory
from _factories.work_slug_redirect.db import WorkSlugRedirectDBFactory
from models._tests.integrity import violated_constraint
from models.work.db import WorkDB
from models.work_slug_redirect.db import WorkSlugRedirectDB

MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc001")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc0ff")


class TestWorkSlugRedirectDB:
    def test_has_the_old_slug_as_its_primary_key_and_no_surrogate_id(self) -> None:
        table = WorkSlugRedirectDB.__table__

        assert [column.name for column in table.primary_key] == ["old_slug"]
        assert "id" not in table.c

    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        WorkDBFactory(id=MSG_ID, slug="mobile-suit-gundam")
        WorkSlugRedirectDBFactory(work_id=MSG_ID, old_slug="gundam-0079")
        test_db_session.commit()
        test_db_session.expunge_all()

        redirect = test_db_session.execute(select(WorkSlugRedirectDB)).scalar_one()

        assert redirect.work_id == MSG_ID
        assert redirect.old_slug == "gundam-0079"
        assert redirect.created_at == mock_utcnow

    def test_deletes_the_redirect_when_the_suit_is_deleted(
        self, test_db_session: Session
    ) -> None:
        WorkDBFactory(id=MSG_ID)
        WorkSlugRedirectDBFactory(work_id=MSG_ID)
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(WorkDB, MSG_ID))
        test_db_session.commit()

        assert test_db_session.scalars(select(WorkSlugRedirectDB)).all() == []

    def test_rejects_a_malformed_old_slug(self, test_db_session: Session) -> None:
        WorkDBFactory(id=MSG_ID)
        WorkSlugRedirectDBFactory(work_id=MSG_ID, old_slug="Gundam_0079")

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_work_slug_redirects_old_slug_format",
        )

    def test_rejects_a_missing_work(self, test_db_session: Session) -> None:
        WorkSlugRedirectDBFactory(work_id=MISSING_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "work_slug_redirects_work_id_fkey",
        )
