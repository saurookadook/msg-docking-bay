import uuid
from datetime import datetime

import pytest
from sqlalchemy import Table, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_relation.db import MobileSuitRelationDBFactory
from _factories.source.db import SourceDBFactory
from constants.catalog import MobileSuitRelationType
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit_relation.db import MobileSuitRelationDB
from models.source.db import SourceDB

ZAKU_II_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b9001")
WORKER_ZAKU_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b9002")
ZAKU_II_KAI_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b9003")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b9004")


@pytest.fixture
def suits(test_db_session: Session) -> None:
    MobileSuitDBFactory(id=ZAKU_II_ID, name="Zaku II")
    MobileSuitDBFactory(id=WORKER_ZAKU_ID, name="Zaku I (Worker)")
    MobileSuitDBFactory(id=ZAKU_II_KAI_ID, name="Zaku II Kai")
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.commit()


def edges(test_db_session: Session) -> list[tuple[uuid.UUID, str, uuid.UUID]]:
    rows = test_db_session.execute(
        text(
            "SELECT from_mobile_suit_id, relation_type::text, to_mobile_suit_id"
            " FROM mobile_suit_relations"
            " ORDER BY from_mobile_suit_id, relation_type"
        )
    )
    return [(from_id, relation, to_id) for (from_id, relation, to_id) in rows]


class TestMobileSuitRelationDBTable:
    def test_has_the_edge_as_its_primary_key_and_no_surrogate_id(self) -> None:
        """A junction table's key is what it joins (RDB-2, RDB-11)."""
        table: Table = BaseDB.metadata.tables["mobile_suit_relations"]

        assert "id" not in table.c
        assert [c.name for c in table.primary_key] == [
            "from_mobile_suit_id",
            "relation_type",
            "to_mobile_suit_id",
        ]
        assert "updated_at" not in table.c


@pytest.mark.usefixtures("suits")
class TestMobileSuitRelationDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            from_mobile_suit_id=ZAKU_II_KAI_ID,
            to_mobile_suit_id=ZAKU_II_ID,
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        relation = test_db_session.execute(select(MobileSuitRelationDB)).scalar_one()

        assert relation.from_mobile_suit_id == ZAKU_II_KAI_ID
        assert relation.relation_type is MobileSuitRelationType.VARIANT_OF
        assert relation.source_id == SOURCE_ID
        assert relation.to_mobile_suit_id == ZAKU_II_ID
        assert relation.created_at == mock_utcnow

    def test_stores_the_relation_type_value(self, test_db_session: Session) -> None:
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            from_mobile_suit_id=ZAKU_II_ID,
            relation_type=MobileSuitRelationType.DEVELOPED_FROM,
            to_mobile_suit_id=WORKER_ZAKU_ID,
        )
        test_db_session.commit()

        assert edges(test_db_session) == [
            (ZAKU_II_ID, "developed_from", WORKER_ZAKU_ID)
        ]

    def test_allows_several_relation_types_between_one_pair(
        self, test_db_session: Session
    ) -> None:
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            from_mobile_suit_id=ZAKU_II_KAI_ID,
            relation_type=MobileSuitRelationType.VARIANT_OF,
            to_mobile_suit_id=ZAKU_II_ID,
        )
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            from_mobile_suit_id=ZAKU_II_KAI_ID,
            relation_type=MobileSuitRelationType.UPGRADE_OF,
            to_mobile_suit_id=ZAKU_II_ID,
        )

        test_db_session.flush()

    @pytest.mark.parametrize("deleted_id", [ZAKU_II_KAI_ID, ZAKU_II_ID])
    def test_deletes_the_edge_when_either_suit_is_deleted(
        self, test_db_session: Session, deleted_id: uuid.UUID
    ) -> None:
        """ON DELETE CASCADE on both ends: an edge needs both suits."""
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            from_mobile_suit_id=ZAKU_II_KAI_ID,
            to_mobile_suit_id=ZAKU_II_ID,
        )
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(MobileSuitDB, deleted_id))
        test_db_session.commit()

        assert edges(test_db_session) == []


@pytest.mark.usefixtures("suits")
class TestMobileSuitRelationDBConstraints:
    def test_rejects_a_duplicate_edge(self, test_db_session: Session) -> None:
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            from_mobile_suit_id=ZAKU_II_KAI_ID,
            to_mobile_suit_id=ZAKU_II_ID,
        )
        test_db_session.commit()
        test_db_session.expunge_all()
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            from_mobile_suit_id=ZAKU_II_KAI_ID,
            to_mobile_suit_id=ZAKU_II_ID,
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "mobile_suit_relations_pkey",
        )

    def test_rejects_a_suit_related_to_itself(self, test_db_session: Session) -> None:
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            from_mobile_suit_id=ZAKU_II_ID,
            to_mobile_suit_id=ZAKU_II_ID,
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_mobile_suit_relations_not_self_relation",
        )

    @pytest.mark.parametrize(
        "end, constraint",
        [
            ("from_mobile_suit_id", "mobile_suit_relations_from_mobile_suit_id_fkey"),
            ("to_mobile_suit_id", "mobile_suit_relations_to_mobile_suit_id_fkey"),
        ],
    )
    def test_rejects_a_missing_suit(
        self, test_db_session: Session, end: str, constraint: str
    ) -> None:
        missing = uuid.UUID("019a1984-0750-7142-aedd-75291c5b90ff")
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            **{
                "from_mobile_suit_id": ZAKU_II_KAI_ID,
                "to_mobile_suit_id": ZAKU_II_ID,
                end: missing,
            },
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    def test_rejects_a_missing_source(self, test_db_session: Session) -> None:
        MobileSuitRelationDBFactory(
            source_id=uuid.UUID("019a1984-0750-7142-aedd-75291c5b90fe"),
            from_mobile_suit_id=ZAKU_II_KAI_ID,
            to_mobile_suit_id=ZAKU_II_ID,
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "mobile_suit_relations_source_id_fkey",
        )

    def test_blocks_deleting_a_source_an_edge_cites(
        self, test_db_session: Session
    ) -> None:
        """RESTRICT: provenance cannot vanish from under an edge."""
        MobileSuitRelationDBFactory(
            source_id=SOURCE_ID,
            from_mobile_suit_id=ZAKU_II_KAI_ID,
            to_mobile_suit_id=ZAKU_II_ID,
        )
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(SourceDB, SOURCE_ID))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == (
            "23001",
            "mobile_suit_relations_source_id_fkey",
        )
