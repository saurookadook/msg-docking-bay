import uuid
from datetime import datetime

import pytest
from sqlalchemy import Table, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from _factories.work_relation.db import WorkRelationDBFactory
from constants.catalog import WorkRelationType
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.source.db import SourceDB
from models.work.db import WorkDB
from models.work_relation.db import WorkRelationDB

MSG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8001")
ZETA_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8002")
MSG_I_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8003")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b8004")


@pytest.fixture
def works(test_db_session: Session) -> None:
    WorkDBFactory(id=MSG_ID, title="Mobile Suit Gundam")
    WorkDBFactory(id=ZETA_ID, title="Mobile Suit Zeta Gundam")
    WorkDBFactory(id=MSG_I_ID, title="Mobile Suit Gundam I")
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.commit()


def edges(test_db_session: Session) -> list[tuple[uuid.UUID, str, uuid.UUID]]:
    rows = test_db_session.execute(
        text(
            "SELECT from_work_id, relation_type::text, to_work_id"
            " FROM work_relations ORDER BY from_work_id, relation_type"
        )
    )
    return [(from_id, relation, to_id) for (from_id, relation, to_id) in rows]


class TestWorkRelationDBTable:
    def test_has_the_edge_as_its_primary_key_and_no_surrogate_id(self) -> None:
        """A junction table's key is what it joins (RDB-2, RDB-11)."""
        table: Table = BaseDB.metadata.tables["work_relations"]

        assert "id" not in table.c
        assert [c.name for c in table.primary_key] == [
            "from_work_id",
            "relation_type",
            "to_work_id",
        ]
        assert "updated_at" not in table.c


@pytest.mark.usefixtures("works")
class TestWorkRelationDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        WorkRelationDBFactory(
            source_id=SOURCE_ID, from_work_id=ZETA_ID, to_work_id=MSG_ID
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        relation = test_db_session.execute(select(WorkRelationDB)).scalar_one()

        assert relation.from_work_id == ZETA_ID
        assert relation.relation_type is WorkRelationType.SEQUEL_OF
        assert relation.source_id == SOURCE_ID
        assert relation.to_work_id == MSG_ID
        assert relation.created_at == mock_utcnow

    def test_stores_the_relation_type_value(self, test_db_session: Session) -> None:
        WorkRelationDBFactory(
            source_id=SOURCE_ID,
            from_work_id=MSG_I_ID,
            relation_type=WorkRelationType.COMPILATION_OF,
            to_work_id=MSG_ID,
        )
        test_db_session.commit()

        assert edges(test_db_session) == [(MSG_I_ID, "compilation_of", MSG_ID)]

    def test_allows_several_relation_types_between_one_pair(
        self, test_db_session: Session
    ) -> None:
        WorkRelationDBFactory(
            source_id=SOURCE_ID,
            from_work_id=MSG_I_ID,
            relation_type=WorkRelationType.COMPILATION_OF,
            to_work_id=MSG_ID,
        )
        WorkRelationDBFactory(
            source_id=SOURCE_ID,
            from_work_id=MSG_I_ID,
            relation_type=WorkRelationType.ADAPTATION_OF,
            to_work_id=MSG_ID,
        )

        test_db_session.flush()

    @pytest.mark.parametrize("deleted_id", [ZETA_ID, MSG_ID])
    def test_deletes_the_edge_when_either_work_is_deleted(
        self, test_db_session: Session, deleted_id: uuid.UUID
    ) -> None:
        """ON DELETE CASCADE on both ends: an edge needs both works."""
        WorkRelationDBFactory(
            source_id=SOURCE_ID, from_work_id=ZETA_ID, to_work_id=MSG_ID
        )
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(WorkDB, deleted_id))
        test_db_session.commit()

        assert edges(test_db_session) == []


@pytest.mark.usefixtures("works")
class TestWorkRelationDBConstraints:
    def test_rejects_a_duplicate_edge(self, test_db_session: Session) -> None:
        WorkRelationDBFactory(
            source_id=SOURCE_ID, from_work_id=ZETA_ID, to_work_id=MSG_ID
        )
        test_db_session.commit()
        test_db_session.expunge_all()
        WorkRelationDBFactory(
            source_id=SOURCE_ID, from_work_id=ZETA_ID, to_work_id=MSG_ID
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23505", "work_relations_pkey")

    def test_rejects_a_work_related_to_itself(self, test_db_session: Session) -> None:
        WorkRelationDBFactory(
            source_id=SOURCE_ID, from_work_id=MSG_ID, to_work_id=MSG_ID
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_work_relations_not_self_relation",
        )

    @pytest.mark.parametrize(
        "end, constraint",
        [
            ("from_work_id", "work_relations_from_work_id_fkey"),
            ("to_work_id", "work_relations_to_work_id_fkey"),
        ],
    )
    def test_rejects_a_missing_work(
        self, test_db_session: Session, end: str, constraint: str
    ) -> None:
        missing = uuid.UUID("019a1984-0750-7142-aedd-75291c5b80ff")
        WorkRelationDBFactory(
            source_id=SOURCE_ID,
            **{"from_work_id": ZETA_ID, "to_work_id": MSG_ID, end: missing},
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    def test_rejects_a_missing_source(self, test_db_session: Session) -> None:
        WorkRelationDBFactory(
            source_id=uuid.UUID("019a1984-0750-7142-aedd-75291c5b80fe"),
            from_work_id=ZETA_ID,
            to_work_id=MSG_ID,
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "work_relations_source_id_fkey",
        )

    def test_blocks_deleting_a_source_an_edge_cites(
        self, test_db_session: Session
    ) -> None:
        """RESTRICT: provenance cannot vanish from under an edge."""
        WorkRelationDBFactory(
            source_id=SOURCE_ID, from_work_id=ZETA_ID, to_work_id=MSG_ID
        )
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(SourceDB, SOURCE_ID))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == (
            "23001",
            "work_relations_source_id_fkey",
        )
