import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.character.db import CharacterDBFactory
from _factories.character_slug_redirect.db import CharacterSlugRedirectDBFactory
from models._tests.integrity import violated_constraint
from models.character.db import CharacterDB
from models.character_slug_redirect.db import CharacterSlugRedirectDB

ENTITY_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc001")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc0ff")


class TestCharacterSlugRedirectDB:
    def test_has_the_old_slug_as_its_primary_key_and_no_surrogate_id(self) -> None:
        table = CharacterSlugRedirectDB.__table__

        assert [column.name for column in table.primary_key] == ["old_slug"]
        assert "id" not in table.c

    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        CharacterDBFactory(id=ENTITY_ID, slug="amuro-ray")
        CharacterSlugRedirectDBFactory(
            character_id=ENTITY_ID, old_slug="amuro-ray-0079"
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        redirect = test_db_session.execute(select(CharacterSlugRedirectDB)).scalar_one()

        assert redirect.character_id == ENTITY_ID
        assert redirect.old_slug == "amuro-ray-0079"
        assert redirect.created_at == mock_utcnow

    def test_deletes_the_redirect_when_the_character_is_deleted(
        self, test_db_session: Session
    ) -> None:
        CharacterDBFactory(id=ENTITY_ID)
        CharacterSlugRedirectDBFactory(character_id=ENTITY_ID)
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(CharacterDB, ENTITY_ID))
        test_db_session.commit()

        assert test_db_session.scalars(select(CharacterSlugRedirectDB)).all() == []

    def test_rejects_a_malformed_old_slug(self, test_db_session: Session) -> None:
        CharacterDBFactory(id=ENTITY_ID)
        CharacterSlugRedirectDBFactory(character_id=ENTITY_ID, old_slug="Amuro_0079")

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_character_slug_redirects_old_slug_format",
        )

    def test_rejects_a_missing_character(self, test_db_session: Session) -> None:
        CharacterSlugRedirectDBFactory(character_id=MISSING_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "character_slug_redirects_character_id_fkey",
        )
