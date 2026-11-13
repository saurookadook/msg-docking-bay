import uuid
from datetime import datetime

import pytest
from sqlalchemy import Table, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.character.db import CharacterDBFactory
from _factories.character_appearance.db import CharacterAppearanceDBFactory
from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.character.db import CharacterDB
from models.character_appearance.db import CharacterAppearanceDB
from models.source.db import SourceDB
from models.work.db import WorkDB

CHARACTER_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0d00001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0d00002")
ZETA_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0d00003")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0d00004")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0d000ff")


@pytest.fixture
def character_and_works(test_db_session: Session) -> None:
    CharacterDBFactory(id=CHARACTER_ID, name="Amuro Ray")
    WorkDBFactory(id=MSG_ID, title="Mobile Suit Gundam")
    WorkDBFactory(id=ZETA_ID, title="Mobile Suit Zeta Gundam")
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.commit()


def appear(**overrides: uuid.UUID) -> None:
    CharacterAppearanceDBFactory(
        **{
            "character_id": CHARACTER_ID,
            "source_id": SOURCE_ID,
            "work_id": MSG_ID,
            **overrides,
        }
    )


def appearance_count(test_db_session: Session) -> int:
    return test_db_session.execute(
        text("SELECT count(*) FROM character_appearances")
    ).scalar_one()


class TestCharacterAppearanceDBTable:
    def test_has_the_pair_as_its_primary_key_and_no_surrogate_id(self) -> None:
        """A junction table's key is what it joins (RDB-2, RDB-11)."""
        table: Table = BaseDB.metadata.tables["character_appearances"]

        assert "id" not in table.c
        assert [c.name for c in table.primary_key] == ["character_id", "work_id"]
        assert "updated_at" not in table.c


@pytest.mark.usefixtures("character_and_works")
class TestCharacterAppearanceDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        appear()
        test_db_session.commit()
        test_db_session.expunge_all()

        appearance = test_db_session.execute(select(CharacterAppearanceDB)).scalar_one()

        assert appearance.character_id == CHARACTER_ID
        assert appearance.source_id == SOURCE_ID
        assert appearance.work_id == MSG_ID
        assert appearance.created_at == mock_utcnow

    def test_allows_one_appearance_in_each_of_several_works(
        self, test_db_session: Session
    ) -> None:
        appear(work_id=MSG_ID)
        appear(work_id=ZETA_ID)

        test_db_session.flush()

    @pytest.mark.parametrize(
        ("deleted", "deleted_id"), [(CharacterDB, CHARACTER_ID), (WorkDB, MSG_ID)]
    )
    def test_deletes_the_appearance_when_the_character_or_work_is_deleted(
        self,
        test_db_session: Session,
        deleted: type[CharacterDB | WorkDB],
        deleted_id: uuid.UUID,
    ) -> None:
        appear()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(deleted, deleted_id))
        test_db_session.commit()

        assert appearance_count(test_db_session) == 0


@pytest.mark.usefixtures("character_and_works")
class TestCharacterAppearanceDBConstraints:
    def test_rejects_a_second_appearance_in_the_same_work(
        self, test_db_session: Session
    ) -> None:
        appear()
        test_db_session.commit()
        test_db_session.expunge_all()
        appear()

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "character_appearances_pkey",
        )

    @pytest.mark.parametrize(
        "column, constraint",
        [
            ("character_id", "character_appearances_character_id_fkey"),
            ("source_id", "character_appearances_source_id_fkey"),
            ("work_id", "character_appearances_work_id_fkey"),
        ],
    )
    def test_rejects_a_missing_reference(
        self, test_db_session: Session, column: str, constraint: str
    ) -> None:
        appear(**{column: MISSING_ID})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    def test_blocks_deleting_a_source_an_appearance_cites(
        self, test_db_session: Session
    ) -> None:
        """RESTRICT: provenance cannot vanish from under it."""
        appear()
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(SourceDB, SOURCE_ID))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == (
            "23001",
            "character_appearances_source_id_fkey",
        )
