import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.armament.db import ArmamentDBFactory
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.armament.db import ArmamentDB

PART_ID = uuid.UUID("019a1984-0750-7142-aedd-75295bd00001")


class TestArmamentDBTable:
    def test_is_named_armaments(self) -> None:
        """The derived name must be the plural the schema uses."""
        assert ArmamentDB.__table__ is BaseDB.metadata.tables["armaments"]


class TestArmamentDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        ArmamentDBFactory(
            id=PART_ID,
            fandom_page_title="60mm Vulcan Gun",
            name="60mm Vulcan Gun",
            slug="60mm-vulcan-gun",
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        part = test_db_session.execute(
            select(ArmamentDB).where(ArmamentDB.id == PART_ID)
        ).scalar_one()

        assert part.fandom_page_title == "60mm Vulcan Gun"
        assert part.name == "60mm Vulcan Gun"
        assert part.slug == "60mm-vulcan-gun"
        assert part.created_at == mock_utcnow
        assert part.updated_at == mock_utcnow

    def test_allows_two_with_the_same_name(self, test_db_session: Session) -> None:
        ArmamentDBFactory(name="60mm Vulcan Gun")
        ArmamentDBFactory(name="60mm Vulcan Gun")

        test_db_session.flush()


class TestArmamentDBConstraints:
    @pytest.mark.parametrize(
        "column, value, constraint",
        [
            ("fandom_page_title", "60mm Vulcan Gun", "armaments_fandom_page_title_key"),
            ("slug", "60mm-vulcan-gun", "armaments_slug_key"),
        ],
    )
    def test_rejects_a_duplicate(
        self, test_db_session: Session, column: str, value: str, constraint: str
    ) -> None:
        ArmamentDBFactory(**{column: value})
        ArmamentDBFactory(**{column: value})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23505", constraint)

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"fandom_page_title": ""}, "ck_armaments_fandom_page_title_not_empty"),
            ({"name": ""}, "ck_armaments_name_not_empty"),
            ({"slug": "60mm_Vulcan_Gun"}, "ck_armaments_slug_format"),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        ArmamentDBFactory(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)
