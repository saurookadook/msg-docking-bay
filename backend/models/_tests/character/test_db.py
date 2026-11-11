import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.character.db import CharacterDBFactory
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.character.db import CharacterDB

AMURO_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0a00001")


class TestCharacterDBTable:
    def test_is_named_characters(self) -> None:
        """The derived name must be the plural the schema uses."""
        assert CharacterDB.__table__ is BaseDB.metadata.tables["characters"]


class TestCharacterDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        CharacterDBFactory(
            id=AMURO_ID,
            fandom_page_title="Amuro Ray",
            name="Amuro Ray",
            name_ja="アムロ・レイ",
            slug="amuro-ray",
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        character = test_db_session.execute(
            select(CharacterDB).where(CharacterDB.id == AMURO_ID)
        ).scalar_one()

        assert character.fandom_page_title == "Amuro Ray"
        assert character.name == "Amuro Ray"
        assert character.name_ja == "アムロ・レイ"
        assert character.slug == "amuro-ray"
        assert character.created_at == mock_utcnow
        assert character.updated_at == mock_utcnow

    def test_generates_a_uuidv7_id_on_the_server(
        self, test_db_session: Session
    ) -> None:
        character = CharacterDB(name="Char Aznable", slug="char-aznable")
        test_db_session.add(character)
        test_db_session.flush()

        assert character.id.version == 7

    def test_allows_two_with_the_same_name(self, test_db_session: Session) -> None:
        """Namesakes are told apart by slug."""
        CharacterDBFactory(name="Kai Shiden")
        CharacterDBFactory(name="Kai Shiden")

        test_db_session.flush()


class TestCharacterDBConstraints:
    @pytest.mark.parametrize(
        "column, value, constraint",
        [
            ("fandom_page_title", "Amuro Ray", "characters_fandom_page_title_key"),
            ("slug", "amuro-ray", "characters_slug_key"),
        ],
    )
    def test_rejects_a_duplicate(
        self, test_db_session: Session, column: str, value: str, constraint: str
    ) -> None:
        CharacterDBFactory(**{column: value})
        CharacterDBFactory(**{column: value})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23505", constraint)

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"fandom_page_title": ""}, "ck_characters_fandom_page_title_not_empty"),
            ({"name": ""}, "ck_characters_name_not_empty"),
            ({"name_ja": ""}, "ck_characters_name_ja_not_empty"),
            ({"slug": "Amuro Ray"}, "ck_characters_slug_format"),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        CharacterDBFactory(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)
