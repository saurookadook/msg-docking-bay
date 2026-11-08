import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.source.db import SourceDBFactory
from _factories.spec_sheet.db import SpecSheetDBFactory
from models._tests.integrity import violated_constraint
from models.mobile_suit.db import MobileSuitDB
from models.source.db import SourceDB
from models.spec_sheet.db import SpecSheetDB

ZETA_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc001")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc002")
OTHER_SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc003")
SHEET_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc004")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc0ff")

MEASUREMENTS = [
    "empty_weight_kg",
    "generator_output_kw",
    "gross_weight_kg",
    "head_height_m",
    "max_acceleration_g",
    "max_speed_kmh",
    "overall_height_m",
    "sensor_range_m",
    "total_thrust_kg",
    "turn_time_s",
]


@pytest.fixture
def suit_and_sources(test_db_session: Session) -> None:
    MobileSuitDBFactory(id=ZETA_ID, name="Zeta Gundam")
    SourceDBFactory(id=SOURCE_ID)
    SourceDBFactory(id=OTHER_SOURCE_ID)
    test_db_session.commit()


def sheet(**overrides: Any) -> None:
    SpecSheetDBFactory(
        **{"mobile_suit_id": ZETA_ID, "source_id": SOURCE_ID, **overrides}
    )


@pytest.mark.usefixtures("suit_and_sources")
class TestSpecSheetDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        sheet(
            id=SHEET_ID,
            configuration="Waverider",
            empty_weight_kg=28_700.0,
            generator_output_kw=2_020.0,
            gross_weight_kg=62_300.0,
            head_height_m=19.85,
            max_acceleration_g=1.5,
            max_speed_kmh=7_200.0,
            overall_height_m=21.5,
            raw_infobox={"headheight": "19.85~MS mode", "armor": "Gundarium"},
            sensor_range_m=16_200.0,
            total_thrust_kg=112_600.0,
            turn_time_s=1.8,
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        row = test_db_session.execute(
            select(SpecSheetDB).where(SpecSheetDB.id == SHEET_ID)
        ).scalar_one()

        assert row.configuration == "Waverider"
        assert row.empty_weight_kg == pytest.approx(28_700.0, rel=1e-6)
        assert row.generator_output_kw == pytest.approx(2_020.0, rel=1e-6)
        assert row.gross_weight_kg == pytest.approx(62_300.0, rel=1e-6)
        assert row.head_height_m == pytest.approx(19.85, rel=1e-6)
        assert row.max_acceleration_g == pytest.approx(1.5, rel=1e-6)
        assert row.max_speed_kmh == pytest.approx(7_200.0, rel=1e-6)
        assert row.mobile_suit_id == ZETA_ID
        assert row.overall_height_m == pytest.approx(21.5, rel=1e-6)
        assert row.raw_infobox == {"headheight": "19.85~MS mode", "armor": "Gundarium"}
        assert row.sensor_range_m == pytest.approx(16_200.0, rel=1e-6)
        assert row.source_id == SOURCE_ID
        assert row.total_thrust_kg == pytest.approx(112_600.0, rel=1e-6)
        assert row.turn_time_s == pytest.approx(1.8, rel=1e-6)
        assert row.created_at == mock_utcnow
        assert row.updated_at == mock_utcnow

    def test_defaults_raw_infobox_to_an_empty_object(
        self, test_db_session: Session
    ) -> None:
        """The server default applies when an insert omits it."""
        test_db_session.execute(
            text(
                "INSERT INTO spec_sheets (mobile_suit_id, source_id)"
                " VALUES (:suit, :source)"
            ),
            {"suit": ZETA_ID, "source": SOURCE_ID},
        )

        raw = test_db_session.execute(
            text("SELECT raw_infobox FROM spec_sheets")
        ).scalar_one()

        assert raw == {}

    def test_allows_a_named_configuration_beside_the_base_sheet(
        self, test_db_session: Session
    ) -> None:
        sheet(configuration=None)
        sheet(configuration="Waverider")

        test_db_session.flush()

    def test_allows_a_base_sheet_from_each_source(
        self, test_db_session: Session
    ) -> None:
        """A second source adds its own sheets (ADR 0002)."""
        sheet(source_id=SOURCE_ID)
        sheet(source_id=OTHER_SOURCE_ID)

        test_db_session.flush()

    def test_deletes_the_sheets_when_the_suit_is_deleted(
        self, test_db_session: Session
    ) -> None:
        sheet()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(MobileSuitDB, ZETA_ID))
        test_db_session.commit()

        count = test_db_session.execute(
            text("SELECT count(*) FROM spec_sheets")
        ).scalar_one()
        assert count == 0


@pytest.mark.usefixtures("suit_and_sources")
class TestSpecSheetDBConstraints:
    def test_rejects_a_second_base_sheet_for_one_suit_and_source(
        self, test_db_session: Session
    ) -> None:
        """NULLS NOT DISTINCT: two NULL configurations collide."""
        sheet(configuration=None)
        sheet(configuration=None)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "spec_sheets_mobile_suit_id_source_id_configuration_key",
        )

    def test_rejects_a_repeated_configuration(self, test_db_session: Session) -> None:
        sheet(configuration="Waverider")
        sheet(configuration="Waverider")

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "spec_sheets_mobile_suit_id_source_id_configuration_key",
        )

    @pytest.mark.parametrize("column", MEASUREMENTS)
    @pytest.mark.parametrize("value", [0.0, -1.0])
    def test_rejects_a_measurement_that_is_not_positive(
        self, test_db_session: Session, column: str, value: float
    ) -> None:
        sheet(**{column: value})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            f"ck_spec_sheets_{column}_positive",
        )

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"configuration": ""}, "ck_spec_sheets_configuration_not_empty"),
            ({"raw_infobox": ["headheight"]}, "ck_spec_sheets_raw_infobox_is_object"),
            ({"raw_infobox": "19.85"}, "ck_spec_sheets_raw_infobox_is_object"),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        sheet(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)

    @pytest.mark.parametrize(
        "column, constraint",
        [
            ("mobile_suit_id", "spec_sheets_mobile_suit_id_fkey"),
            ("source_id", "spec_sheets_source_id_fkey"),
        ],
    )
    def test_rejects_a_missing_reference(
        self, test_db_session: Session, column: str, constraint: str
    ) -> None:
        sheet(**{column: MISSING_ID})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    def test_blocks_deleting_a_source_a_sheet_cites(
        self, test_db_session: Session
    ) -> None:
        """RESTRICT: provenance cannot vanish from under a sheet."""
        sheet()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(SourceDB, SOURCE_ID))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == (
            "23001",
            "spec_sheets_source_id_fkey",
        )
