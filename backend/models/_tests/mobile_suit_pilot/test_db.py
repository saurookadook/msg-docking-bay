import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import Table, delete, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.character.db import CharacterDBFactory
from _factories.character_appearance.db import CharacterAppearanceDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_appearance.db import MobileSuitAppearanceDBFactory
from _factories.mobile_suit_pilot.db import MobileSuitPilotDBFactory
from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.character.db import CharacterDB
from models.character_appearance.db import CharacterAppearanceDB
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit_appearance.db import MobileSuitAppearanceDB
from models.mobile_suit_pilot.db import MobileSuitPilotDB
from models.source.db import SourceDB

AMURO_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0f00001")
GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0f00002")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0f00003")
ZETA_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0f00004")
ORIGIN_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0f00005")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0f00006")
PILOT_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0f00007")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0f000ff")


@pytest.fixture
def amuro_and_gundam(test_db_session: Session) -> None:
    """Both appear in MSG; Amuro alone in Zeta, the Gundam in Origin."""
    CharacterDBFactory(id=AMURO_ID, name="Amuro Ray")
    MobileSuitDBFactory(id=GUNDAM_ID, name="Gundam")
    WorkDBFactory(id=MSG_ID, title="Mobile Suit Gundam")
    WorkDBFactory(id=ZETA_ID, title="Mobile Suit Zeta Gundam")
    WorkDBFactory(id=ORIGIN_ID, title="Mobile Suit Gundam: The Origin")
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.flush()
    for work_id in (MSG_ID, ZETA_ID):
        CharacterAppearanceDBFactory(
            character_id=AMURO_ID, source_id=SOURCE_ID, work_id=work_id
        )
    for work_id in (MSG_ID, ORIGIN_ID):
        MobileSuitAppearanceDBFactory(
            mobile_suit_id=GUNDAM_ID, source_id=SOURCE_ID, work_id=work_id
        )
    test_db_session.commit()


def pilot(**overrides: Any) -> None:
    MobileSuitPilotDBFactory(
        **{
            "character_id": AMURO_ID,
            "mobile_suit_id": GUNDAM_ID,
            "source_id": SOURCE_ID,
            "work_id": MSG_ID,
            **overrides,
        }
    )


def pilot_works(test_db_session: Session) -> list[uuid.UUID | None]:
    """Each remaining pilot row's work, nulls last."""
    return list(
        test_db_session.execute(
            text("SELECT work_id FROM mobile_suit_pilots ORDER BY work_id")
        ).scalars()
    )


class TestMobileSuitPilotDBTable:
    def test_has_a_surrogate_id_and_no_updated_at(self) -> None:
        """The RDB-2 deviation: a nullable ``work_id`` is not a key."""
        table: Table = BaseDB.metadata.tables["mobile_suit_pilots"]

        assert [c.name for c in table.primary_key] == ["id"]
        assert table.c.work_id.nullable is True
        assert "updated_at" not in table.c


@pytest.mark.usefixtures("amuro_and_gundam")
class TestMobileSuitPilotDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        pilot(id=PILOT_ID)
        test_db_session.commit()
        test_db_session.expunge_all()

        row = test_db_session.execute(select(MobileSuitPilotDB)).scalar_one()

        assert row.id == PILOT_ID
        assert row.character_id == AMURO_ID
        assert row.mobile_suit_id == GUNDAM_ID
        assert row.source_id == SOURCE_ID
        assert row.work_id == MSG_ID
        assert row.created_at == mock_utcnow

    def test_accepts_a_pilot_with_no_work(self, test_db_session: Session) -> None:
        """MATCH SIMPLE: a null ``work_id`` needs no appearance."""
        pilot(work_id=None)

        test_db_session.flush()

    def test_allows_a_no_work_row_beside_a_work_row(
        self, test_db_session: Session
    ) -> None:
        pilot(work_id=None)
        pilot(work_id=MSG_ID)

        test_db_session.flush()

    def test_deletes_pilot_rows_when_a_character_appearance_is_deleted(
        self, test_db_session: Session
    ) -> None:
        """The no-work row relies on no appearance, so it stays."""
        pilot(work_id=MSG_ID)
        pilot(work_id=None)
        test_db_session.commit()

        test_db_session.execute(
            delete(CharacterAppearanceDB).where(CharacterAppearanceDB.work_id == MSG_ID)
        )
        test_db_session.commit()

        assert pilot_works(test_db_session) == [None]

    def test_deletes_pilot_rows_when_a_suit_appearance_is_deleted(
        self, test_db_session: Session
    ) -> None:
        pilot(work_id=MSG_ID)
        pilot(work_id=None)
        test_db_session.commit()

        test_db_session.execute(
            delete(MobileSuitAppearanceDB).where(
                MobileSuitAppearanceDB.work_id == MSG_ID
            )
        )
        test_db_session.commit()

        assert pilot_works(test_db_session) == [None]

    @pytest.mark.parametrize("deleted", [CharacterDB, MobileSuitDB])
    def test_deletes_every_pilot_row_when_the_character_or_suit_is_deleted(
        self, test_db_session: Session, deleted: type[CharacterDB | MobileSuitDB]
    ) -> None:
        """The plain FK removes the no-work row too."""
        pilot(work_id=MSG_ID)
        pilot(work_id=None)
        test_db_session.commit()

        deleted_id = AMURO_ID if deleted is CharacterDB else GUNDAM_ID
        test_db_session.delete(test_db_session.get_one(deleted, deleted_id))
        test_db_session.commit()

        assert pilot_works(test_db_session) == []


@pytest.mark.usefixtures("amuro_and_gundam")
class TestMobileSuitPilotDBConstraints:
    @pytest.mark.parametrize("work_id", [MSG_ID, None])
    def test_rejects_a_duplicate_pilot_row(
        self, test_db_session: Session, work_id: uuid.UUID | None
    ) -> None:
        """NULLS NOT DISTINCT: one no-work row per pilot and suit."""
        pilot(work_id=work_id)
        test_db_session.commit()
        pilot(work_id=work_id)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "mobile_suit_pilots_character_id_mobile_suit_id_work_id_key",
        )

    @pytest.mark.parametrize(
        "work_id, constraint",
        [
            # The Gundam is not in Zeta; Amuro is not in The Origin.
            (ZETA_ID, "mobile_suit_pilots_mobile_suit_id_work_id_fkey"),
            (ORIGIN_ID, "mobile_suit_pilots_character_id_work_id_fkey"),
        ],
    )
    def test_rejects_a_work_without_both_appearances(
        self, test_db_session: Session, work_id: uuid.UUID, constraint: str
    ) -> None:
        pilot(work_id=work_id)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    @pytest.mark.parametrize(
        "column, constraint",
        [
            ("character_id", "mobile_suit_pilots_character_id_fkey"),
            ("mobile_suit_id", "mobile_suit_pilots_mobile_suit_id_fkey"),
            ("source_id", "mobile_suit_pilots_source_id_fkey"),
        ],
    )
    def test_rejects_a_missing_reference_with_no_work(
        self, test_db_session: Session, column: str, constraint: str
    ) -> None:
        """The plain FKs check what MATCH SIMPLE skips."""
        pilot(**{column: MISSING_ID, "work_id": None})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    def test_blocks_deleting_a_source_a_pilot_row_cites(
        self, test_db_session: Session
    ) -> None:
        """RESTRICT: provenance cannot vanish from under it.

        The appearances cite the same source, so the pilot row's
        RESTRICT is checked with no appearance in the way.
        """
        other_source = SourceDBFactory()
        test_db_session.flush()
        pilot(source_id=other_source.id)
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(SourceDB, other_source.id))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == (
            "23001",
            "mobile_suit_pilots_source_id_fkey",
        )
