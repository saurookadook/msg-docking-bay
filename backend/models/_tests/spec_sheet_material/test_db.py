import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import Table, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.material.db import MaterialDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.source.db import SourceDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.spec_sheet_material.db import SpecSheetMaterialDBFactory
from constants.catalog import MaterialUse
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.material.db import MaterialDB
from models.spec_sheet.db import SpecSheetDB
from models.spec_sheet_material.db import SpecSheetMaterialDB

PART_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bf00011")
SUIT_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bf00012")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bf00013")
SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bf00014")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bf000ff")


@pytest.fixture
def sheet_and_material(test_db_session: Session) -> None:
    MobileSuitDBFactory(id=SUIT_ID)
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.flush()
    SpecSheetDBFactory(id=SHEET_ID, mobile_suit_id=SUIT_ID, source_id=SOURCE_ID)
    MaterialDBFactory(id=PART_ID, name="Luna Titanium Alloy")
    test_db_session.commit()


def listing(**overrides: Any) -> None:
    SpecSheetMaterialDBFactory(
        **{"material_id": PART_ID, "spec_sheet_id": SHEET_ID, **overrides}
    )


def listing_count(test_db_session: Session) -> int:
    return test_db_session.execute(
        text("SELECT count(*) FROM spec_sheet_materials")
    ).scalar_one()


class TestSpecSheetMaterialDBTable:
    def test_has_the_listing_as_its_primary_key_and_no_surrogate_id(self) -> None:
        """A junction table's key is what it joins (RDB-2, RDB-11)."""
        table: Table = BaseDB.metadata.tables["spec_sheet_materials"]

        assert "id" not in table.c
        assert [c.name for c in table.primary_key] == [
            "material_id",
            "material_use",
            "spec_sheet_id",
        ]
        assert "updated_at" not in table.c

    def test_has_no_source_id(self) -> None:
        """The sheet's source covers the parts it lists (Phase 1)."""
        assert "source_id" not in BaseDB.metadata.tables["spec_sheet_materials"].c


@pytest.mark.usefixtures("sheet_and_material")
class TestSpecSheetMaterialDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        listing(material_use=MaterialUse.FRAME, note="as written in the infobox")
        test_db_session.commit()
        test_db_session.expunge_all()

        row = test_db_session.execute(select(SpecSheetMaterialDB)).scalar_one()

        assert row.material_id == PART_ID
        assert row.note == "as written in the infobox"
        assert row.material_use is MaterialUse.FRAME
        assert row.spec_sheet_id == SHEET_ID
        assert row.created_at == mock_utcnow

    def test_allows_one_material_under_each_material_use(
        self, test_db_session: Session
    ) -> None:
        """``material_use`` is in the key."""
        listing(material_use=MaterialUse.ARMOR)
        listing(material_use=MaterialUse.FRAME)

        test_db_session.flush()

    def test_stores_the_material_use_value(self, test_db_session: Session) -> None:
        listing(material_use=MaterialUse.FRAME)
        test_db_session.commit()

        stored = test_db_session.execute(
            text("SELECT material_use::text FROM spec_sheet_materials")
        ).scalar_one()

        assert stored == "frame"

    def test_deletes_the_listing_when_the_sheet_is_deleted(
        self, test_db_session: Session
    ) -> None:
        listing()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(SpecSheetDB, SHEET_ID))
        test_db_session.commit()

        assert listing_count(test_db_session) == 0


@pytest.mark.usefixtures("sheet_and_material")
class TestSpecSheetMaterialDBConstraints:
    def test_rejects_a_duplicate_listing(self, test_db_session: Session) -> None:
        listing()
        test_db_session.commit()
        test_db_session.expunge_all()
        listing()

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "spec_sheet_materials_pkey",
        )

    def test_rejects_an_empty_note(self, test_db_session: Session) -> None:
        listing(note="")

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_spec_sheet_materials_note_not_empty",
        )

    @pytest.mark.parametrize(
        "column, constraint",
        [
            ("material_id", "spec_sheet_materials_material_id_fkey"),
            ("spec_sheet_id", "spec_sheet_materials_spec_sheet_id_fkey"),
        ],
    )
    def test_rejects_a_missing_reference(
        self, test_db_session: Session, column: str, constraint: str
    ) -> None:
        listing(**{column: MISSING_ID})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    def test_blocks_deleting_a_material_a_sheet_still_lists(
        self, test_db_session: Session
    ) -> None:
        """RESTRICT: a listed part cannot vanish from under a sheet."""
        listing()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(MaterialDB, PART_ID))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == (
            "23001",
            "spec_sheet_materials_material_id_fkey",
        )
