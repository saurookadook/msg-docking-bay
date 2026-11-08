import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import Table, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.armament.db import ArmamentDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.source.db import SourceDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.spec_sheet_armament.db import SpecSheetArmamentDBFactory
from constants.catalog import ArmamentMount
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.armament.db import ArmamentDB
from models.spec_sheet.db import SpecSheetDB
from models.spec_sheet_armament.db import SpecSheetArmamentDB

PART_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bd00011")
SUIT_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bd00012")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bd00013")
SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bd00014")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bd000ff")


@pytest.fixture
def sheet_and_armament(test_db_session: Session) -> None:
    MobileSuitDBFactory(id=SUIT_ID)
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.flush()
    SpecSheetDBFactory(id=SHEET_ID, mobile_suit_id=SUIT_ID, source_id=SOURCE_ID)
    ArmamentDBFactory(id=PART_ID, name="60mm Vulcan Gun")
    test_db_session.commit()


def listing(**overrides: Any) -> None:
    SpecSheetArmamentDBFactory(
        **{"armament_id": PART_ID, "spec_sheet_id": SHEET_ID, **overrides}
    )


def listing_count(test_db_session: Session) -> int:
    return test_db_session.execute(
        text("SELECT count(*) FROM spec_sheet_armaments")
    ).scalar_one()


class TestSpecSheetArmamentDBTable:
    def test_has_the_listing_as_its_primary_key_and_no_surrogate_id(self) -> None:
        """A junction table's key is what it joins (RDB-2, RDB-11)."""
        table: Table = BaseDB.metadata.tables["spec_sheet_armaments"]

        assert "id" not in table.c
        assert [c.name for c in table.primary_key] == [
            "armament_id",
            "mount",
            "spec_sheet_id",
        ]
        assert "updated_at" not in table.c

    def test_has_no_source_id(self) -> None:
        """The sheet's source covers the parts it lists (Phase 1)."""
        assert "source_id" not in BaseDB.metadata.tables["spec_sheet_armaments"].c


@pytest.mark.usefixtures("sheet_and_armament")
class TestSpecSheetArmamentDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        listing(
            mount=ArmamentMount.HANDHELD,
            quantity_max=4,
            quantity_min=2,
            note="as written in the infobox",
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        row = test_db_session.execute(select(SpecSheetArmamentDB)).scalar_one()

        assert row.armament_id == PART_ID
        assert row.note == "as written in the infobox"
        assert row.mount is ArmamentMount.HANDHELD
        assert row.quantity_max == 4
        assert row.quantity_min == 2
        assert row.spec_sheet_id == SHEET_ID
        assert row.created_at == mock_utcnow

    def test_allows_one_weapon_under_each_mount(self, test_db_session: Session) -> None:
        """``mount`` is in the key."""
        listing(mount=ArmamentMount.FIXED)
        listing(mount=ArmamentMount.HANDHELD)

        test_db_session.flush()

    def test_stores_the_mount_value(self, test_db_session: Session) -> None:
        listing(mount=ArmamentMount.HANDHELD)
        test_db_session.commit()

        stored = test_db_session.execute(
            text("SELECT mount::text FROM spec_sheet_armaments")
        ).scalar_one()

        assert stored == "handheld"

    def test_deletes_the_listing_when_the_sheet_is_deleted(
        self, test_db_session: Session
    ) -> None:
        listing()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(SpecSheetDB, SHEET_ID))
        test_db_session.commit()

        assert listing_count(test_db_session) == 0


@pytest.mark.usefixtures("sheet_and_armament")
class TestSpecSheetArmamentDBConstraints:
    def test_rejects_a_duplicate_listing(self, test_db_session: Session) -> None:
        listing()
        test_db_session.commit()
        test_db_session.expunge_all()
        listing()

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "spec_sheet_armaments_pkey",
        )

    def test_rejects_an_empty_note(self, test_db_session: Session) -> None:
        listing(note="")

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_spec_sheet_armaments_note_not_empty",
        )

    @pytest.mark.parametrize(
        "overrides",
        [{"quantity_min": 2}, {"quantity_min": 2, "quantity_max": 2}],
    )
    def test_accepts_an_exact_quantity(
        self, test_db_session: Session, overrides: dict[str, Any]
    ) -> None:
        listing(**overrides)

        test_db_session.flush()

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"quantity_min": 0}, "ck_spec_sheet_armaments_quantity_min_positive"),
            (
                {"quantity_min": 4, "quantity_max": 2},
                "ck_spec_sheet_armaments_quantities_in_order",
            ),
            (
                {"quantity_max": 2},
                "ck_spec_sheet_armaments_quantity_max_needs_quantity_min",
            ),
        ],
    )
    def test_rejects_an_invalid_quantity(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        listing(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)

    @pytest.mark.parametrize(
        "column, constraint",
        [
            ("armament_id", "spec_sheet_armaments_armament_id_fkey"),
            ("spec_sheet_id", "spec_sheet_armaments_spec_sheet_id_fkey"),
        ],
    )
    def test_rejects_a_missing_reference(
        self, test_db_session: Session, column: str, constraint: str
    ) -> None:
        listing(**{column: MISSING_ID})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    def test_blocks_deleting_a_weapon_a_sheet_still_lists(
        self, test_db_session: Session
    ) -> None:
        """RESTRICT: a listed part cannot vanish from under a sheet."""
        listing()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(ArmamentDB, PART_ID))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == (
            "23001",
            "spec_sheet_armaments_armament_id_fkey",
        )
