import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import Table, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_appearance.db import MobileSuitAppearanceDBFactory
from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit_appearance.db import MobileSuitAppearanceDB
from models.source.db import SourceDB
from models.work.db import WorkDB

GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bb001")
MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bb002")
ORIGIN_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bb003")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bb004")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bb0ff")


@pytest.fixture
def suit_and_works(test_db_session: Session) -> None:
    MobileSuitDBFactory(id=GUNDAM_ID, name="Gundam")
    WorkDBFactory(id=MSG_ID, title="Mobile Suit Gundam")
    WorkDBFactory(id=ORIGIN_ID, title="Mobile Suit Gundam: The Origin")
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.commit()


def appear(**overrides: Any) -> None:
    MobileSuitAppearanceDBFactory(
        **{
            "mobile_suit_id": GUNDAM_ID,
            "source_id": SOURCE_ID,
            "work_id": MSG_ID,
            **overrides,
        }
    )


def appearance_count(test_db_session: Session) -> int:
    return test_db_session.execute(
        text("SELECT count(*) FROM mobile_suit_appearances")
    ).scalar_one()


class TestMobileSuitAppearanceDBTable:
    def test_has_the_pair_as_its_primary_key_and_no_surrogate_id(self) -> None:
        """A junction table's key is what it joins (RDB-2, RDB-11)."""
        table: Table = BaseDB.metadata.tables["mobile_suit_appearances"]

        assert "id" not in table.c
        assert [c.name for c in table.primary_key] == ["mobile_suit_id", "work_id"]
        assert "updated_at" not in table.c


@pytest.mark.usefixtures("suit_and_works")
class TestMobileSuitAppearanceDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        appear(first_episode=1, is_debut=True, last_episode=43)
        test_db_session.commit()
        test_db_session.expunge_all()

        appearance = test_db_session.execute(
            select(MobileSuitAppearanceDB)
        ).scalar_one()

        assert appearance.first_episode == 1
        assert appearance.is_debut is True
        assert appearance.last_episode == 43
        assert appearance.mobile_suit_id == GUNDAM_ID
        assert appearance.source_id == SOURCE_ID
        assert appearance.work_id == MSG_ID
        assert appearance.created_at == mock_utcnow

    def test_defaults_to_not_a_debut(self, test_db_session: Session) -> None:
        """The server default applies when an insert omits it."""
        test_db_session.execute(
            text(
                "INSERT INTO mobile_suit_appearances"
                " (mobile_suit_id, source_id, work_id)"
                " VALUES (:suit, :source, :work)"
            ),
            {"suit": GUNDAM_ID, "source": SOURCE_ID, "work": MSG_ID},
        )

        is_debut = test_db_session.execute(
            text("SELECT is_debut FROM mobile_suit_appearances")
        ).scalar_one()

        assert is_debut is False

    def test_allows_a_debut_in_two_works(self, test_db_session: Session) -> None:
        """A manga and an anime can introduce a suit at once."""
        appear(is_debut=True, work_id=MSG_ID)
        appear(is_debut=True, work_id=ORIGIN_ID)

        test_db_session.flush()

    def test_accepts_a_single_episode(self, test_db_session: Session) -> None:
        """A first episode alone, or equal bounds, is one episode."""
        appear(first_episode=12, work_id=MSG_ID)
        appear(first_episode=5, last_episode=5, work_id=ORIGIN_ID)

        test_db_session.flush()

    @pytest.mark.parametrize("deleted", [MobileSuitDB, WorkDB])
    def test_deletes_the_appearance_when_the_suit_or_work_is_deleted(
        self, test_db_session: Session, deleted: type[MobileSuitDB | WorkDB]
    ) -> None:
        appear()
        test_db_session.commit()

        deleted_id = GUNDAM_ID if deleted is MobileSuitDB else MSG_ID
        test_db_session.delete(test_db_session.get_one(deleted, deleted_id))
        test_db_session.commit()

        assert appearance_count(test_db_session) == 0


@pytest.mark.usefixtures("suit_and_works")
class TestMobileSuitAppearanceDBConstraints:
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
            "mobile_suit_appearances_pkey",
        )

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"first_episode": 0}, "ck_mobile_suit_appearances_first_episode_positive"),
            (
                {"first_episode": 10, "last_episode": 9},
                "ck_mobile_suit_appearances_episodes_in_order",
            ),
            (
                {"last_episode": 9},
                "ck_mobile_suit_appearances_last_episode_needs_first",
            ),
        ],
    )
    def test_rejects_an_invalid_episode_range(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        appear(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)

    @pytest.mark.parametrize(
        "column, constraint",
        [
            ("mobile_suit_id", "mobile_suit_appearances_mobile_suit_id_fkey"),
            ("source_id", "mobile_suit_appearances_source_id_fkey"),
            ("work_id", "mobile_suit_appearances_work_id_fkey"),
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
            "mobile_suit_appearances_source_id_fkey",
        )
