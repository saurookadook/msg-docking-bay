import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from constants.catalog import UnitType
from models._tests.integrity import violated_constraint
from models.mobile_suit.db import MobileSuitDB

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7001")
RX_78_2_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b7002")


class TestMobileSuitDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        ContinuityDBFactory(id=UC_ID)
        MobileSuitDBFactory(
            id=RX_78_2_ID,
            continuity_id=UC_ID,
            fandom_page_id=2034,
            model_number="RX-78-2",
            name="Gundam",
            name_ja="ガンダム",
            slug="rx-78-2-gundam",
            unit_type=UnitType.SUIT,
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        suit = test_db_session.execute(
            select(MobileSuitDB).where(MobileSuitDB.id == RX_78_2_ID)
        ).scalar_one()

        assert suit.continuity_id == UC_ID
        assert suit.fandom_page_id == 2034
        assert suit.model_number == "RX-78-2"
        assert suit.name == "Gundam"
        assert suit.name_ja == "ガンダム"
        assert suit.slug == "rx-78-2-gundam"
        assert suit.unit_type is UnitType.SUIT
        assert suit.created_at == mock_utcnow
        assert suit.updated_at == mock_utcnow

    def test_stores_the_unit_type_value_not_the_member_name(
        self, test_db_session: Session
    ) -> None:
        """SQLAlchemy stores enum names by default (SQLA-11)."""
        MobileSuitDBFactory(id=RX_78_2_ID, unit_type=UnitType.MAN_MACHINE)
        test_db_session.commit()

        stored = test_db_session.execute(
            text("SELECT unit_type::text FROM mobile_suits WHERE id = :id"),
            {"id": RX_78_2_ID},
        ).scalar_one()

        assert stored == "man_machine"

    def test_clears_the_continuity_when_the_continuity_is_deleted(
        self, test_db_session: Session
    ) -> None:
        uc = ContinuityDBFactory(id=UC_ID)
        MobileSuitDBFactory(id=RX_78_2_ID, continuity_id=UC_ID)
        test_db_session.commit()

        test_db_session.delete(uc)
        test_db_session.commit()
        test_db_session.expunge_all()

        assert test_db_session.get_one(MobileSuitDB, RX_78_2_ID).continuity_id is None

    def test_allows_two_suits_with_the_same_name_and_model_number(
        self, test_db_session: Session
    ) -> None:
        """Versions of one unit share both: RX-78-2 and its Ver.Ka."""
        MobileSuitDBFactory(model_number="RX-78-2", name="Gundam")
        MobileSuitDBFactory(model_number="RX-78-2", name="Gundam")

        test_db_session.flush()


class TestMobileSuitDBConstraints:
    @pytest.mark.parametrize(
        "column, value, constraint",
        [
            ("fandom_page_id", 2034, "mobile_suits_fandom_page_id_key"),
            ("slug", "rx-78-2-gundam", "mobile_suits_slug_key"),
        ],
    )
    def test_rejects_a_duplicate(
        self, test_db_session: Session, column: str, value: int | str, constraint: str
    ) -> None:
        MobileSuitDBFactory(**{column: value})
        MobileSuitDBFactory(**{column: value})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23505", constraint)

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"fandom_page_id": 0}, "ck_mobile_suits_fandom_page_id_positive"),
            ({"model_number": ""}, "ck_mobile_suits_model_number_not_empty"),
            ({"name": ""}, "ck_mobile_suits_name_not_empty"),
            ({"name_ja": ""}, "ck_mobile_suits_name_ja_not_empty"),
            ({"slug": "RX-78-2_Gundam"}, "ck_mobile_suits_slug_format"),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        MobileSuitDBFactory(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)

    def test_rejects_a_missing_continuity(self, test_db_session: Session) -> None:
        MobileSuitDBFactory(
            continuity_id=uuid.UUID("019a1984-0750-7142-aedd-75291c5b70ff")
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "mobile_suits_continuity_id_fkey",
        )
