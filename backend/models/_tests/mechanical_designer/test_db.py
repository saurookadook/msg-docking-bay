import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.mechanical_designer.db import MechanicalDesignerDB

OKAWARA_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0c00001")


class TestMechanicalDesignerDBTable:
    def test_is_named_mechanical_designers(self) -> None:
        """The derived name must be the plural the schema uses."""
        assert (
            MechanicalDesignerDB.__table__
            is BaseDB.metadata.tables["mechanical_designers"]
        )


class TestMechanicalDesignerDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        MechanicalDesignerDBFactory(
            id=OKAWARA_ID,
            fandom_page_title="Kunio Okawara",
            name="Kunio Okawara",
            name_ja="大河原邦男",
            slug="kunio-okawara",
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        designer = test_db_session.execute(
            select(MechanicalDesignerDB).where(MechanicalDesignerDB.id == OKAWARA_ID)
        ).scalar_one()

        assert designer.fandom_page_title == "Kunio Okawara"
        assert designer.name == "Kunio Okawara"
        assert designer.name_ja == "大河原邦男"
        assert designer.slug == "kunio-okawara"
        assert designer.created_at == mock_utcnow
        assert designer.updated_at == mock_utcnow

    def test_generates_a_uuidv7_id_on_the_server(
        self, test_db_session: Session
    ) -> None:
        designer = MechanicalDesignerDB(name="Hajime Katoki", slug="hajime-katoki")
        test_db_session.add(designer)
        test_db_session.flush()

        assert designer.id.version == 7

    def test_allows_two_with_the_same_name(self, test_db_session: Session) -> None:
        """Namesakes are told apart by slug."""
        MechanicalDesignerDBFactory(name="Makoto Kobayashi")
        MechanicalDesignerDBFactory(name="Makoto Kobayashi")

        test_db_session.flush()


class TestMechanicalDesignerDBConstraints:
    @pytest.mark.parametrize(
        "column, value, constraint",
        [
            (
                "fandom_page_title",
                "Kunio Okawara",
                "mechanical_designers_fandom_page_title_key",
            ),
            ("slug", "kunio-okawara", "mechanical_designers_slug_key"),
        ],
    )
    def test_rejects_a_duplicate(
        self, test_db_session: Session, column: str, value: str, constraint: str
    ) -> None:
        MechanicalDesignerDBFactory(**{column: value})
        MechanicalDesignerDBFactory(**{column: value})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23505", constraint)

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            (
                {"fandom_page_title": ""},
                "ck_mechanical_designers_fandom_page_title_not_empty",
            ),
            ({"name": ""}, "ck_mechanical_designers_name_not_empty"),
            ({"name_ja": ""}, "ck_mechanical_designers_name_ja_not_empty"),
            ({"slug": "Kunio Okawara"}, "ck_mechanical_designers_slug_format"),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        MechanicalDesignerDBFactory(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)
