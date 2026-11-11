import uuid
from datetime import datetime

import pytest
from sqlalchemy import Table, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_designer.db import MobileSuitDesignerDBFactory
from _factories.source.db import SourceDBFactory
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.mechanical_designer.db import MechanicalDesignerDB
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit_designer.db import MobileSuitDesignerDB
from models.source.db import SourceDB

OKAWARA_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1100001")
KATOKI_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1100002")
GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1100003")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1100004")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c11000ff")


@pytest.fixture
def designers_and_suit(test_db_session: Session) -> None:
    MechanicalDesignerDBFactory(id=OKAWARA_ID, name="Kunio Okawara")
    MechanicalDesignerDBFactory(id=KATOKI_ID, name="Hajime Katoki")
    MobileSuitDBFactory(id=GUNDAM_ID, name="Gundam")
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.commit()


def credit(**overrides: uuid.UUID) -> None:
    MobileSuitDesignerDBFactory(
        **{
            "mechanical_designer_id": OKAWARA_ID,
            "mobile_suit_id": GUNDAM_ID,
            "source_id": SOURCE_ID,
            **overrides,
        }
    )


def credit_count(test_db_session: Session) -> int:
    return test_db_session.execute(
        text("SELECT count(*) FROM mobile_suit_designers")
    ).scalar_one()


class TestMobileSuitDesignerDBTable:
    def test_has_the_pair_as_its_primary_key_and_no_surrogate_id(self) -> None:
        """A junction table's key is what it joins (RDB-2, RDB-11)."""
        table: Table = BaseDB.metadata.tables["mobile_suit_designers"]

        assert "id" not in table.c
        assert [c.name for c in table.primary_key] == [
            "mechanical_designer_id",
            "mobile_suit_id",
        ]
        assert "updated_at" not in table.c


@pytest.mark.usefixtures("designers_and_suit")
class TestMobileSuitDesignerDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        credit()
        test_db_session.commit()
        test_db_session.expunge_all()

        row = test_db_session.execute(select(MobileSuitDesignerDB)).scalar_one()

        assert row.mechanical_designer_id == OKAWARA_ID
        assert row.mobile_suit_id == GUNDAM_ID
        assert row.source_id == SOURCE_ID
        assert row.created_at == mock_utcnow

    def test_allows_several_designers_for_one_suit(
        self, test_db_session: Session
    ) -> None:
        credit(mechanical_designer_id=OKAWARA_ID)
        credit(mechanical_designer_id=KATOKI_ID)

        test_db_session.flush()

    def test_deletes_the_credits_when_the_suit_is_deleted(
        self, test_db_session: Session
    ) -> None:
        credit()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(MobileSuitDB, GUNDAM_ID))
        test_db_session.commit()

        assert credit_count(test_db_session) == 0


@pytest.mark.usefixtures("designers_and_suit")
class TestMobileSuitDesignerDBConstraints:
    def test_rejects_a_second_credit_for_the_same_pair(
        self, test_db_session: Session
    ) -> None:
        credit()
        test_db_session.commit()
        test_db_session.expunge_all()
        credit()

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "mobile_suit_designers_pkey",
        )

    @pytest.mark.parametrize(
        "column, constraint",
        [
            (
                "mechanical_designer_id",
                "mobile_suit_designers_mechanical_designer_id_fkey",
            ),
            ("mobile_suit_id", "mobile_suit_designers_mobile_suit_id_fkey"),
            ("source_id", "mobile_suit_designers_source_id_fkey"),
        ],
    )
    def test_rejects_a_missing_reference(
        self, test_db_session: Session, column: str, constraint: str
    ) -> None:
        credit(**{column: MISSING_ID})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    @pytest.mark.parametrize(
        "deleted, constraint",
        [
            (MechanicalDesignerDB, "mobile_suit_designers_mechanical_designer_id_fkey"),
            (SourceDB, "mobile_suit_designers_source_id_fkey"),
        ],
    )
    def test_blocks_deleting_a_designer_or_source_a_credit_cites(
        self,
        test_db_session: Session,
        deleted: type[MechanicalDesignerDB | SourceDB],
        constraint: str,
    ) -> None:
        """RESTRICT: a credit cannot lose its designer or provenance."""
        credit()
        test_db_session.commit()

        deleted_id = OKAWARA_ID if deleted is MechanicalDesignerDB else SOURCE_ID
        test_db_session.delete(test_db_session.get_one(deleted, deleted_id))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == ("23001", constraint)
