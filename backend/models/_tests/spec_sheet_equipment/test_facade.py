import uuid
from collections.abc import Sequence
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from _factories.equipment.db import EquipmentDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.spec_sheet_equipment.db import SpecSheetEquipmentDBFactory
from constants.catalog import EquipmentFit
from models._tests.query_count import CountStatements
from models._tests.spec_sheet_parts import (
    SHEET_ID,
    SOURCE_ID,
    SUIT_ID,
    seed_sheet,
)
from models.spec_sheet_equipment.entity import EquipmentListingEntity
from models.spec_sheet_equipment.facade import SpecSheetEquipmentFacade

FIRST_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4220001")
SECOND_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4220002")
OTHER_SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4220003")
EMPTY_SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4220004")
SAME_A_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4220005")
SAME_B_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4220006")


@pytest.fixture
def parts(test_db_session: Session) -> None:
    """Two parts and three sheets of one suit, the last one empty."""
    seed_sheet(test_db_session)
    EquipmentDBFactory(id=FIRST_ID, name="Core Block System")
    EquipmentDBFactory(id=SECOND_ID, name="Magnet Coating")
    for sheet_id, configuration in (
        (OTHER_SHEET_ID, "Other"),
        (EMPTY_SHEET_ID, "Empty"),
    ):
        SpecSheetDBFactory(
            id=sheet_id,
            configuration=configuration,
            mobile_suit_id=SUIT_ID,
            source_id=SOURCE_ID,
        )
    test_db_session.flush()


def names(listings: Sequence[EquipmentListingEntity]) -> list[str]:
    return [listing.equipment.name for listing in listings]


@pytest.mark.usefixtures("parts")
class TestSpecSheetEquipmentFacadeGetForSheets:
    def test_get_for_sheets_sends_no_statement_for_no_sheets(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """A suit without sheets costs nothing here (PYTEST-24)."""
        facade = SpecSheetEquipmentFacade(db_session=test_db_session)

        with count_statements() as count:
            result = facade.get_for_sheets([])

        assert (result, count.value) == ({}, 0)

    def test_get_for_sheets_groups_every_sheet_in_one_statement(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """Each sheet given has a key, empty when it lists nothing."""
        SpecSheetEquipmentDBFactory(equipment_id=FIRST_ID, spec_sheet_id=SHEET_ID)
        SpecSheetEquipmentDBFactory(equipment_id=FIRST_ID, spec_sheet_id=OTHER_SHEET_ID)
        SpecSheetEquipmentDBFactory(
            equipment_id=SECOND_ID, spec_sheet_id=OTHER_SHEET_ID
        )
        test_db_session.flush()
        facade = SpecSheetEquipmentFacade(db_session=test_db_session)

        with count_statements() as count:
            result = facade.get_for_sheets([SHEET_ID, OTHER_SHEET_ID, EMPTY_SHEET_ID])

        assert count.value == 1
        assert {sheet_id: names(listings) for sheet_id, listings in result.items()} == {
            SHEET_ID: ["Core Block System"],
            OTHER_SHEET_ID: ["Core Block System", "Magnet Coating"],
            EMPTY_SHEET_ID: [],
        }

    def test_get_for_sheets_orders_by_fit_then_name(
        self, test_db_session: Session
    ) -> None:
        """The enum sorts in its declared order, then the name."""
        for part_id, fit in (
            (SECOND_ID, EquipmentFit.OPTIONAL),
            (FIRST_ID, EquipmentFit.OPTIONAL),
            (SECOND_ID, EquipmentFit.STANDARD),
        ):
            SpecSheetEquipmentDBFactory(
                equipment_id=part_id, fit=fit, spec_sheet_id=SHEET_ID
            )
        test_db_session.flush()

        listings = SpecSheetEquipmentFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert [(listing.fit, listing.equipment.name) for listing in listings] == [
            (EquipmentFit.STANDARD, "Magnet Coating"),
            (EquipmentFit.OPTIONAL, "Core Block System"),
            (EquipmentFit.OPTIONAL, "Magnet Coating"),
        ]

    def test_get_for_sheets_orders_a_name_tie_by_slug(
        self, test_db_session: Session
    ) -> None:
        """Names repeat, so the slug is the last key (RDB-22)."""
        for part_id, slug in ((SAME_B_ID, "same-b"), (SAME_A_ID, "same-a")):
            EquipmentDBFactory(id=part_id, name="Same", slug=slug)
        test_db_session.flush()
        for part_id in (SAME_B_ID, SAME_A_ID):
            SpecSheetEquipmentDBFactory(equipment_id=part_id, spec_sheet_id=SHEET_ID)
        test_db_session.flush()

        listings = SpecSheetEquipmentFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert [listing.equipment.slug for listing in listings] == ["same-a", "same-b"]

    def test_get_for_sheets_serves_the_listing_with_a_ref(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """The part is a ref, and the listing keeps its own columns."""
        SpecSheetEquipmentDBFactory(
            equipment_id=FIRST_ID,
            note="field upgrade",
            spec_sheet_id=SHEET_ID,
        )
        test_db_session.flush()

        (listing,) = SpecSheetEquipmentFacade(
            db_session=test_db_session
        ).get_for_sheets([SHEET_ID])[SHEET_ID]

        assert listing.model_dump() == {
            "created_at": mock_utcnow,
            "fit": EquipmentFit.STANDARD,
            "equipment": {"name": "Core Block System", "slug": listing.equipment.slug},
            "note": "field upgrade",
        }


@pytest.mark.usefixtures("parts")
class TestSpecSheetEquipmentFacadeCreateOrUpdate:
    def test_create_or_update_on_its_key(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """A rerun with a new note updates the listing in place."""
        facade = SpecSheetEquipmentFacade(db_session=test_db_session)
        payload = {
            "equipment_id": FIRST_ID,
            "fit": EquipmentFit.STANDARD,
            "spec_sheet_id": SHEET_ID,
            "note": None,
        }

        created = facade.create_or_update(payload=payload)
        noted = facade.create_or_update(payload={**payload, "note": "refit"})

        assert (created.note, noted.note) == (None, "refit")
        assert noted.created_at == created.created_at != mock_utcnow
