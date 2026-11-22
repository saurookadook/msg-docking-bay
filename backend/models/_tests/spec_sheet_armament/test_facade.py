import uuid
from collections.abc import Sequence
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from _factories.armament.db import ArmamentDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.spec_sheet_armament.db import SpecSheetArmamentDBFactory
from constants.catalog import ArmamentMount
from models._tests.query_count import CountStatements
from models._tests.spec_sheet_parts import (
    SHEET_ID,
    SOURCE_ID,
    SUIT_ID,
    seed_sheet,
)
from models.spec_sheet_armament.entity import ArmamentListingEntity
from models.spec_sheet_armament.facade import SpecSheetArmamentFacade

FIRST_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4210001")
SECOND_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4210002")
OTHER_SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4210003")
EMPTY_SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4210004")
SAME_A_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4210005")
SAME_B_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4210006")


@pytest.fixture
def parts(test_db_session: Session) -> None:
    """Two parts and three sheets of one suit, the last one empty."""
    seed_sheet(test_db_session)
    ArmamentDBFactory(id=FIRST_ID, name="Beam Rifle")
    ArmamentDBFactory(id=SECOND_ID, name="Beam Saber")
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


def names(listings: Sequence[ArmamentListingEntity]) -> list[str]:
    return [listing.armament.name for listing in listings]


@pytest.mark.usefixtures("parts")
class TestSpecSheetArmamentFacadeGetForSheets:
    def test_sends_no_statement_for_no_sheets(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """A suit without sheets costs nothing here (PYTEST-24)."""
        facade = SpecSheetArmamentFacade(db_session=test_db_session)

        with count_statements() as count:
            result = facade.get_for_sheets([])

        assert (result, count.value) == ({}, 0)

    def test_groups_every_sheet_in_one_statement(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """Each sheet given has a key, empty when it lists nothing."""
        SpecSheetArmamentDBFactory(armament_id=FIRST_ID, spec_sheet_id=SHEET_ID)
        SpecSheetArmamentDBFactory(armament_id=FIRST_ID, spec_sheet_id=OTHER_SHEET_ID)
        SpecSheetArmamentDBFactory(armament_id=SECOND_ID, spec_sheet_id=OTHER_SHEET_ID)
        test_db_session.flush()
        facade = SpecSheetArmamentFacade(db_session=test_db_session)

        with count_statements() as count:
            result = facade.get_for_sheets([SHEET_ID, OTHER_SHEET_ID, EMPTY_SHEET_ID])

        assert count.value == 1
        assert {sheet_id: names(listings) for sheet_id, listings in result.items()} == {
            SHEET_ID: ["Beam Rifle"],
            OTHER_SHEET_ID: ["Beam Rifle", "Beam Saber"],
            EMPTY_SHEET_ID: [],
        }

    def test_orders_by_mount_then_name(self, test_db_session: Session) -> None:
        """The enum sorts in its declared order, then the name."""
        for part_id, mount in (
            (SECOND_ID, ArmamentMount.HANDHELD),
            (FIRST_ID, ArmamentMount.HANDHELD),
            (SECOND_ID, ArmamentMount.FIXED),
        ):
            SpecSheetArmamentDBFactory(
                armament_id=part_id, mount=mount, spec_sheet_id=SHEET_ID
            )
        test_db_session.flush()

        listings = SpecSheetArmamentFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert [(listing.mount, listing.armament.name) for listing in listings] == [
            (ArmamentMount.FIXED, "Beam Saber"),
            (ArmamentMount.HANDHELD, "Beam Rifle"),
            (ArmamentMount.HANDHELD, "Beam Saber"),
        ]

    def test_orders_a_name_tie_by_slug(self, test_db_session: Session) -> None:
        """Names repeat, so the slug is the last key (RDB-22)."""
        for part_id, slug in ((SAME_B_ID, "same-b"), (SAME_A_ID, "same-a")):
            ArmamentDBFactory(id=part_id, name="Same", slug=slug)
        test_db_session.flush()
        for part_id in (SAME_B_ID, SAME_A_ID):
            SpecSheetArmamentDBFactory(armament_id=part_id, spec_sheet_id=SHEET_ID)
        test_db_session.flush()

        listings = SpecSheetArmamentFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert [listing.armament.slug for listing in listings] == ["same-a", "same-b"]

    def test_serves_the_listing_with_a_ref(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """The part is a ref, and the listing keeps its own columns."""
        SpecSheetArmamentDBFactory(
            armament_id=FIRST_ID,
            note="field upgrade",
            quantity_max=2,
            quantity_min=1,
            spec_sheet_id=SHEET_ID,
        )
        test_db_session.flush()

        (listing,) = SpecSheetArmamentFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert listing.model_dump() == {
            "created_at": mock_utcnow,
            "mount": ArmamentMount.FIXED,
            "armament": {"name": "Beam Rifle", "slug": listing.armament.slug},
            "note": "field upgrade",
            "quantity_max": 2,
            "quantity_min": 1,
        }
