import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.orm import Session

from _factories.powerplant.db import PowerplantDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from _factories.spec_sheet_powerplant.db import SpecSheetPowerplantDBFactory
from models._tests.query_count import CountStatements
from models._tests.spec_sheet_parts import (
    SHEET_ID,
    SOURCE_ID,
    SUIT_ID,
    seed_sheet,
)
from models.spec_sheet_powerplant.facade import SpecSheetPowerplantFacade

if TYPE_CHECKING:
    from models.spec_sheet_powerplant.entity import PowerplantListingEntity

FIRST_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4240001")
SECOND_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4240002")
OTHER_SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4240003")
EMPTY_SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4240004")
SAME_A_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4240005")
SAME_B_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4240006")
ALPHA_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4240007")
ZETA_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c4240008")


@pytest.fixture
def parts(test_db_session: Session) -> None:
    """Two parts and three sheets of one suit, the last one empty."""
    seed_sheet(test_db_session)
    PowerplantDBFactory(id=FIRST_ID, name="Minovsky Ultracompact Fusion Reactor")
    PowerplantDBFactory(id=SECOND_ID, name="Ultracompact Energy Battery")
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


def names(listings: Sequence[PowerplantListingEntity]) -> list[str]:
    return [listing.powerplant.name for listing in listings]


@pytest.mark.usefixtures("parts")
class TestSpecSheetPowerplantFacadeGetForSheets:
    def test_get_for_sheets_sends_no_statement_for_no_sheets(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """A suit without sheets costs nothing here (PYTEST-24)."""
        facade = SpecSheetPowerplantFacade(db_session=test_db_session)

        with count_statements() as count:
            result = facade.get_for_sheets([])

        assert (result, count.value) == ({}, 0)

    def test_get_for_sheets_groups_every_sheet_in_one_statement(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        """Each sheet given has a key, empty when it lists nothing."""
        SpecSheetPowerplantDBFactory(powerplant_id=FIRST_ID, spec_sheet_id=SHEET_ID)
        SpecSheetPowerplantDBFactory(
            powerplant_id=FIRST_ID, spec_sheet_id=OTHER_SHEET_ID
        )
        SpecSheetPowerplantDBFactory(
            powerplant_id=SECOND_ID, spec_sheet_id=OTHER_SHEET_ID
        )
        test_db_session.flush()
        facade = SpecSheetPowerplantFacade(db_session=test_db_session)

        with count_statements() as count:
            result = facade.get_for_sheets([SHEET_ID, OTHER_SHEET_ID, EMPTY_SHEET_ID])

        assert count.value == 1
        assert {sheet_id: names(listings) for sheet_id, listings in result.items()} == {
            SHEET_ID: ["Minovsky Ultracompact Fusion Reactor"],
            OTHER_SHEET_ID: [
                "Minovsky Ultracompact Fusion Reactor",
                "Ultracompact Energy Battery",
            ],
            EMPTY_SHEET_ID: [],
        }

    def test_get_for_sheets_orders_by_name(self, test_db_session: Session) -> None:
        """By name first, though the slugs sort the other way (Q6)."""
        for part_id, name, slug in (
            (ZETA_ID, "Zeta", "a-zeta"),
            (ALPHA_ID, "Alpha", "z-alpha"),
        ):
            PowerplantDBFactory(id=part_id, name=name, slug=slug)
        test_db_session.flush()
        for part_id in (ZETA_ID, ALPHA_ID):
            SpecSheetPowerplantDBFactory(powerplant_id=part_id, spec_sheet_id=SHEET_ID)
        test_db_session.flush()

        listings = SpecSheetPowerplantFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert names(listings) == ["Alpha", "Zeta"]

    def test_get_for_sheets_orders_a_name_tie_by_slug(
        self, test_db_session: Session
    ) -> None:
        """Names repeat, so the slug is the last key (RDB-22)."""
        for part_id, slug in ((SAME_B_ID, "same-b"), (SAME_A_ID, "same-a")):
            PowerplantDBFactory(id=part_id, name="Same", slug=slug)
        test_db_session.flush()
        for part_id in (SAME_B_ID, SAME_A_ID):
            SpecSheetPowerplantDBFactory(powerplant_id=part_id, spec_sheet_id=SHEET_ID)
        test_db_session.flush()

        listings = SpecSheetPowerplantFacade(db_session=test_db_session).get_for_sheets(
            [SHEET_ID]
        )[SHEET_ID]

        assert [listing.powerplant.slug for listing in listings] == ["same-a", "same-b"]

    def test_get_for_sheets_serves_the_listing_with_a_ref(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """The part is a ref, and the listing keeps its own columns."""
        SpecSheetPowerplantDBFactory(
            powerplant_id=FIRST_ID,
            note="field upgrade",
            quantity_max=2,
            quantity_min=1,
            spec_sheet_id=SHEET_ID,
        )
        test_db_session.flush()

        (listing,) = SpecSheetPowerplantFacade(
            db_session=test_db_session
        ).get_for_sheets([SHEET_ID])[SHEET_ID]

        assert listing.model_dump() == {
            "created_at": mock_utcnow,
            "powerplant": {
                "name": "Minovsky Ultracompact Fusion Reactor",
                "slug": listing.powerplant.slug,
            },
            "note": "field upgrade",
            "quantity_max": 2,
            "quantity_min": 1,
        }


@pytest.mark.usefixtures("parts")
class TestSpecSheetPowerplantFacadeCreateOrUpdate:
    def test_create_or_update_on_its_key(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """A rerun with a new note updates the listing in place."""
        facade = SpecSheetPowerplantFacade(db_session=test_db_session)
        payload = {
            "powerplant_id": FIRST_ID,
            "spec_sheet_id": SHEET_ID,
            "quantity_max": None,
            "quantity_min": None,
            "note": None,
        }

        created = facade.create_or_update(payload=payload)
        noted = facade.create_or_update(payload={**payload, "note": "refit"})

        assert (created.note, noted.note) == (None, "refit")
        assert noted.created_at == created.created_at != mock_utcnow
