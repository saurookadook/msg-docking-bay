import uuid
from collections.abc import Sequence
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from _factories.material.db import MaterialDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.spec_sheet_material.db import SpecSheetMaterialDBFactory
from constants.catalog import MaterialUse
from models._tests.query_count import CountStatements
from models._tests.spec_sheet_parts import (
    SHEET_ID,
    SOURCE_ID,
    SUIT_ID,
    seed_sheet,
)
from models.spec_sheet_material.entity import MaterialListingEntity
from models.spec_sheet_material.facade import SpecSheetMaterialFacade

FIRST_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4230001")
SECOND_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4230002")
OTHER_SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4230003")
EMPTY_SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4230004")
SAME_A_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4230005")
SAME_B_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4230006")


@pytest.fixture
def parts(test_db_session: Session) -> None:
    """Two parts and three sheets of one suit, the last one empty."""
    seed_sheet(test_db_session)
    MaterialDBFactory(id=FIRST_ID, name="Gundarium Alloy")
    MaterialDBFactory(id=SECOND_ID, name="Luna Titanium Alloy")
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


def names(listings: Sequence[MaterialListingEntity]) -> list[str]:
    return [listing.material.name for listing in listings]


@pytest.mark.usefixtures("parts")
class TestSpecSheetMaterialFacadeGetForSheets:
    def test_sends_no_statement_for_no_sheets(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """A suit without sheets costs nothing here (PYTEST-24)."""
        facade = SpecSheetMaterialFacade(db_session=test_db_session)

        with count_statements() as count:
            result = facade.get_for_sheets([])

        assert (result, count.value) == ({}, 0)

    def test_groups_every_sheet_in_one_statement(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """Each sheet given has a key, empty when it lists nothing."""
        SpecSheetMaterialDBFactory(material_id=FIRST_ID, spec_sheet_id=SHEET_ID)
        SpecSheetMaterialDBFactory(material_id=FIRST_ID, spec_sheet_id=OTHER_SHEET_ID)
        SpecSheetMaterialDBFactory(material_id=SECOND_ID, spec_sheet_id=OTHER_SHEET_ID)
        test_db_session.flush()
        facade = SpecSheetMaterialFacade(db_session=test_db_session)

        with count_statements() as count:
            result = facade.get_for_sheets([SHEET_ID, OTHER_SHEET_ID, EMPTY_SHEET_ID])

        assert count.value == 1
        assert {sheet_id: names(listings) for sheet_id, listings in result.items()} == {
            SHEET_ID: ["Gundarium Alloy"],
            OTHER_SHEET_ID: ["Gundarium Alloy", "Luna Titanium Alloy"],
            EMPTY_SHEET_ID: [],
        }

    def test_orders_by_material_use_then_name(self, test_db_session: Session) -> None:
        """The enum sorts in its declared order, then the name."""
        for part_id, material_use in (
            (SECOND_ID, MaterialUse.FRAME),
            (FIRST_ID, MaterialUse.FRAME),
            (SECOND_ID, MaterialUse.ARMOR),
        ):
            SpecSheetMaterialDBFactory(
                material_id=part_id, material_use=material_use, spec_sheet_id=SHEET_ID
            )
        test_db_session.flush()

        listings = SpecSheetMaterialFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert [
            (listing.material_use, listing.material.name) for listing in listings
        ] == [
            (MaterialUse.ARMOR, "Luna Titanium Alloy"),
            (MaterialUse.FRAME, "Gundarium Alloy"),
            (MaterialUse.FRAME, "Luna Titanium Alloy"),
        ]

    def test_orders_a_name_tie_by_slug(self, test_db_session: Session) -> None:
        """Names repeat, so the slug is the last key (RDB-22)."""
        for part_id, slug in ((SAME_B_ID, "same-b"), (SAME_A_ID, "same-a")):
            MaterialDBFactory(id=part_id, name="Same", slug=slug)
        test_db_session.flush()
        for part_id in (SAME_B_ID, SAME_A_ID):
            SpecSheetMaterialDBFactory(material_id=part_id, spec_sheet_id=SHEET_ID)
        test_db_session.flush()

        listings = SpecSheetMaterialFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert [listing.material.slug for listing in listings] == ["same-a", "same-b"]

    def test_serves_the_listing_with_a_ref(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """The part is a ref, and the listing keeps its own columns."""
        SpecSheetMaterialDBFactory(
            material_id=FIRST_ID,
            note="field upgrade",
            spec_sheet_id=SHEET_ID,
        )
        test_db_session.flush()

        (listing,) = SpecSheetMaterialFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert listing.model_dump() == {
            "created_at": mock_utcnow,
            "material_use": MaterialUse.ARMOR,
            "material": {"name": "Gundarium Alloy", "slug": listing.material.slug},
            "note": "field upgrade",
        }


@pytest.mark.usefixtures("parts")
class TestSpecSheetMaterialFacadeCreateOrUpdate:
    def test_updates_the_note_on_its_key(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """A rerun with a new note updates the listing in place."""
        facade = SpecSheetMaterialFacade(db_session=test_db_session)
        payload = {
            "material_id": FIRST_ID,
            "material_use": MaterialUse.ARMOR,
            "spec_sheet_id": SHEET_ID,
            "note": None,
        }

        created = facade.create_or_update(payload=payload)
        noted = facade.create_or_update(payload={**payload, "note": "refit"})

        assert (created.note, noted.note) == (None, "refit")
        assert noted.created_at == created.created_at != mock_utcnow
