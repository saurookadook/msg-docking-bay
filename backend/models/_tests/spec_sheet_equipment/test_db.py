import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import Table, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.equipment.db import EquipmentDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.source.db import SourceDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.spec_sheet_equipment.db import SpecSheetEquipmentDBFactory
from constants.catalog import EquipmentFit
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.equipment.db import EquipmentDB
from models.spec_sheet.db import SpecSheetDB
from models.spec_sheet_equipment.db import SpecSheetEquipmentDB

PART_ID = uuid.UUID("019a1984-0750-7142-aedd-75295be00011")
SUIT_ID = uuid.UUID("019a1984-0750-7142-aedd-75295be00012")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75295be00013")
SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-75295be00014")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75295be000ff")


@pytest.fixture
def sheet_and_equipment(test_db_session: Session) -> None:
    MobileSuitDBFactory(id=SUIT_ID)
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.flush()
    SpecSheetDBFactory(id=SHEET_ID, mobile_suit_id=SUIT_ID, source_id=SOURCE_ID)
    EquipmentDBFactory(id=PART_ID, name="Core Block System")
    test_db_session.commit()


def listing(**overrides: Any) -> None:
    SpecSheetEquipmentDBFactory(
        **{"equipment_id": PART_ID, "spec_sheet_id": SHEET_ID, **overrides}
    )


def listing_count(test_db_session: Session) -> int:
    return test_db_session.execute(
        text("SELECT count(*) FROM spec_sheet_equipment")
    ).scalar_one()


class TestSpecSheetEquipmentDBTable:
    def test_has_the_listing_as_its_primary_key_and_no_surrogate_id(self) -> None:
        """A junction table's key is what it joins (RDB-2, RDB-11)."""
        table: Table = BaseDB.metadata.tables["spec_sheet_equipment"]

        assert "id" not in table.c
        assert [c.name for c in table.primary_key] == [
            "equipment_id",
            "fit",
            "spec_sheet_id",
        ]
        assert "updated_at" not in table.c

    def test_has_no_source_id(self) -> None:
        """The sheet's source covers the parts it lists (Phase 1)."""
        assert "source_id" not in BaseDB.metadata.tables["spec_sheet_equipment"].c


@pytest.mark.usefixtures("sheet_and_equipment")
class TestSpecSheetEquipmentDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        listing(fit=EquipmentFit.OPTIONAL, note="as written in the infobox")
        test_db_session.commit()
        test_db_session.expunge_all()

        row = test_db_session.execute(select(SpecSheetEquipmentDB)).scalar_one()

        assert row.equipment_id == PART_ID
        assert row.note == "as written in the infobox"
        assert row.fit is EquipmentFit.OPTIONAL
        assert row.spec_sheet_id == SHEET_ID
        assert row.created_at == mock_utcnow

    def test_allows_one_item_under_each_fit(self, test_db_session: Session) -> None:
        """``fit`` is in the key."""
        listing(fit=EquipmentFit.STANDARD)
        listing(fit=EquipmentFit.OPTIONAL)

        test_db_session.flush()

    def test_stores_the_fit_value(self, test_db_session: Session) -> None:
        listing(fit=EquipmentFit.OPTIONAL)
        test_db_session.commit()

        stored = test_db_session.execute(
            text("SELECT fit::text FROM spec_sheet_equipment")
        ).scalar_one()

        assert stored == "optional"

    def test_deletes_the_listing_when_the_sheet_is_deleted(
        self, test_db_session: Session
    ) -> None:
        listing()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(SpecSheetDB, SHEET_ID))
        test_db_session.commit()

        assert listing_count(test_db_session) == 0


@pytest.mark.usefixtures("sheet_and_equipment")
class TestSpecSheetEquipmentDBConstraints:
    def test_rejects_a_duplicate_listing(self, test_db_session: Session) -> None:
        listing()
        test_db_session.commit()
        test_db_session.expunge_all()
        listing()

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "spec_sheet_equipment_pkey",
        )

    def test_rejects_an_empty_note(self, test_db_session: Session) -> None:
        listing(note="")

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_spec_sheet_equipment_note_not_empty",
        )

    @pytest.mark.parametrize(
        "column, constraint",
        [
            ("equipment_id", "spec_sheet_equipment_equipment_id_fkey"),
            ("spec_sheet_id", "spec_sheet_equipment_spec_sheet_id_fkey"),
        ],
    )
    def test_rejects_a_missing_reference(
        self, test_db_session: Session, column: str, constraint: str
    ) -> None:
        listing(**{column: MISSING_ID})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    def test_blocks_deleting_a_item_a_sheet_still_lists(
        self, test_db_session: Session
    ) -> None:
        """RESTRICT: a listed part cannot vanish from under a sheet."""
        listing()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(EquipmentDB, PART_ID))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == (
            "23001",
            "spec_sheet_equipment_equipment_id_fkey",
        )
