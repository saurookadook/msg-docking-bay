import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_slug_redirect.db import MobileSuitSlugRedirectDBFactory
from models._tests.integrity import violated_constraint
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit_slug_redirect.db import MobileSuitSlugRedirectDB

GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc001")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc0ff")


class TestMobileSuitSlugRedirectDB:
    def test_has_the_old_slug_as_its_primary_key_and_no_surrogate_id(self) -> None:
        table = MobileSuitSlugRedirectDB.__table__

        assert [column.name for column in table.primary_key] == ["old_slug"]
        assert "id" not in table.c

    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        MobileSuitDBFactory(id=GUNDAM_ID, slug="rx-78-2-gundam")
        MobileSuitSlugRedirectDBFactory(
            mobile_suit_id=GUNDAM_ID, old_slug="gundam-rx-78-2"
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        redirect = test_db_session.execute(
            select(MobileSuitSlugRedirectDB)
        ).scalar_one()

        assert redirect.mobile_suit_id == GUNDAM_ID
        assert redirect.old_slug == "gundam-rx-78-2"
        assert redirect.created_at == mock_utcnow

    def test_deletes_the_redirect_when_the_suit_is_deleted(
        self, test_db_session: Session
    ) -> None:
        MobileSuitDBFactory(id=GUNDAM_ID)
        MobileSuitSlugRedirectDBFactory(mobile_suit_id=GUNDAM_ID)
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(MobileSuitDB, GUNDAM_ID))
        test_db_session.commit()

        assert test_db_session.scalars(select(MobileSuitSlugRedirectDB)).all() == []

    def test_rejects_a_malformed_old_slug(self, test_db_session: Session) -> None:
        MobileSuitDBFactory(id=GUNDAM_ID)
        MobileSuitSlugRedirectDBFactory(mobile_suit_id=GUNDAM_ID, old_slug="RX_78_2")

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_mobile_suit_slug_redirects_old_slug_format",
        )

    def test_rejects_a_missing_suit(self, test_db_session: Session) -> None:
        MobileSuitSlugRedirectDBFactory(mobile_suit_id=MISSING_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "mobile_suit_slug_redirects_mobile_suit_id_fkey",
        )
