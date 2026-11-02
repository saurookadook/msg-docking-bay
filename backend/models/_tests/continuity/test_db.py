import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from models._tests.integrity import violated_constraint
from models.continuity.db import ContinuityDB

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b5ada")
GQ_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b5adb")


class TestContinuityDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        ContinuityDBFactory(
            id=UC_ID, name="Universal Century", slug="universal-century"
        )
        ContinuityDBFactory(
            id=GQ_ID,
            name="Universal Century (GQ)",
            parent_continuity_id=UC_ID,
            slug="universal-century-gq",
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        gq = test_db_session.execute(
            select(ContinuityDB).where(ContinuityDB.id == GQ_ID)
        ).scalar_one()

        assert gq.name == "Universal Century (GQ)"
        assert gq.parent_continuity_id == UC_ID
        assert gq.slug == "universal-century-gq"
        assert gq.created_at == mock_utcnow
        assert gq.updated_at == mock_utcnow

    def test_generates_a_uuidv7_id_and_timestamps_on_the_server(
        self, test_db_session: Session
    ) -> None:
        continuity = ContinuityDB(name="Cosmic Era", slug="cosmic-era")
        test_db_session.add(continuity)
        test_db_session.flush()

        assert continuity.id.version == 7
        assert continuity.created_at.tzinfo is not None

    def test_clears_the_parent_link_when_the_parent_is_deleted(
        self, test_db_session: Session
    ) -> None:
        """ON DELETE SET NULL: a branch outlives its parent timeline."""
        uc = ContinuityDBFactory(id=UC_ID)
        ContinuityDBFactory(id=GQ_ID, parent_continuity_id=UC_ID)
        test_db_session.commit()

        test_db_session.delete(uc)
        test_db_session.commit()
        test_db_session.expunge_all()

        gq = test_db_session.get_one(ContinuityDB, GQ_ID)
        assert gq.parent_continuity_id is None


class TestContinuityDBConstraints:
    @pytest.mark.parametrize(
        "column, constraint",
        [
            ("name", "continuities_name_key"),
            ("slug", "continuities_slug_key"),
        ],
    )
    def test_rejects_a_duplicate(
        self, test_db_session: Session, column: str, constraint: str
    ) -> None:
        ContinuityDBFactory(**{column: "after-colony"})
        ContinuityDBFactory(**{column: "after-colony"})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23505", constraint)

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"name": ""}, "ck_continuities_name_not_empty"),
            ({"slug": "Universal Century"}, "ck_continuities_slug_format"),
            ({"slug": "universal--century"}, "ck_continuities_slug_format"),
            ({"slug": "-universal-century"}, "ck_continuities_slug_format"),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, str], constraint: str
    ) -> None:
        ContinuityDBFactory(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)

    def test_rejects_a_continuity_that_is_its_own_parent(
        self, test_db_session: Session
    ) -> None:
        ContinuityDBFactory(id=UC_ID, parent_continuity_id=UC_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_continuities_not_own_parent",
        )
