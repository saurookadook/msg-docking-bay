"""Walk lineages over ``mobile_suit_relations`` with ``WITH RECURSIVE``.

These prove the edge design (ADR 0002): families come from recursive
queries, and the ``CYCLE`` clause stops a walk that loops. The queries
live here until Phase 3a moves them into the mobile suit facade.
"""

import uuid
from typing import Final

import pytest
from sqlalchemy import TextClause, text
from sqlalchemy.orm import Session

from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_relation.db import MobileSuitRelationDBFactory
from _factories.source.db import SourceDBFactory
from constants.catalog import MobileSuitRelationType

GM_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba001")
ZAKU_II_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba002")
WORKER_ZAKU_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba003")
HI_ZACK_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba004")
MARASAI_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba005")
GELGOOG_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba006")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5ba007")

# An edge reads "from is a <type> of to", so a descendant is on the
# ``from`` end and an ancestor on the ``to`` end. Two fixed statements
# rather than one built per direction: SQL is never assembled from
# strings (SQLA-24).
DESCENDANTS: Final[TextClause] = text(
    """
    WITH RECURSIVE lineage (mobile_suit_id) AS (
        SELECT CAST(:root AS uuid)
        UNION ALL
        SELECT r.from_mobile_suit_id
        FROM lineage l
        JOIN mobile_suit_relations r ON r.to_mobile_suit_id = l.mobile_suit_id
    ) CYCLE mobile_suit_id SET is_cycle USING path
    SELECT DISTINCT mobile_suit_id FROM lineage
    WHERE NOT is_cycle AND mobile_suit_id <> CAST(:root AS uuid)
    """
)
ANCESTORS: Final[TextClause] = text(
    """
    WITH RECURSIVE lineage (mobile_suit_id) AS (
        SELECT CAST(:root AS uuid)
        UNION ALL
        SELECT r.to_mobile_suit_id
        FROM lineage l
        JOIN mobile_suit_relations r ON r.from_mobile_suit_id = l.mobile_suit_id
    ) CYCLE mobile_suit_id SET is_cycle USING path
    SELECT DISTINCT mobile_suit_id FROM lineage
    WHERE NOT is_cycle AND mobile_suit_id <> CAST(:root AS uuid)
    """
)


def walk(
    test_db_session: Session, query: TextClause, root: uuid.UUID
) -> set[uuid.UUID]:
    return set(test_db_session.execute(query, {"root": root}).scalars())


def link(
    from_id: uuid.UUID, relation_type: MobileSuitRelationType, to_id: uuid.UUID
) -> None:
    MobileSuitRelationDBFactory(
        from_mobile_suit_id=from_id,
        relation_type=relation_type,
        source_id=SOURCE_ID,
        to_mobile_suit_id=to_id,
    )


@pytest.fixture
def zaku_and_gm_lines(test_db_session: Session) -> None:
    """Build two lines that meet at the Hi-Zack, plus an outsider.

    Worker Zaku → Zaku II (variant_of); Hi-Zack → Zaku II and GM
    (developed_from); Marasai → Hi-Zack (developed_from). The Gelgoog
    has no edges.
    """
    for suit_id, name in [
        (GM_ID, "GM"),
        (ZAKU_II_ID, "Zaku II"),
        (WORKER_ZAKU_ID, "Zaku I (Worker)"),
        (HI_ZACK_ID, "Hi-Zack"),
        (MARASAI_ID, "Marasai"),
        (GELGOOG_ID, "Gelgoog"),
    ]:
        MobileSuitDBFactory(id=suit_id, name=name)
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.flush()
    link(WORKER_ZAKU_ID, MobileSuitRelationType.VARIANT_OF, ZAKU_II_ID)
    link(HI_ZACK_ID, MobileSuitRelationType.DEVELOPED_FROM, ZAKU_II_ID)
    link(HI_ZACK_ID, MobileSuitRelationType.DEVELOPED_FROM, GM_ID)
    link(MARASAI_ID, MobileSuitRelationType.DEVELOPED_FROM, HI_ZACK_ID)
    test_db_session.commit()


@pytest.mark.usefixtures("zaku_and_gm_lines")
class TestMobileSuitLineage:
    def test_finds_every_descendant_through_several_generations(
        self, test_db_session: Session
    ) -> None:
        assert walk(test_db_session, DESCENDANTS, ZAKU_II_ID) == {
            WORKER_ZAKU_ID,
            HI_ZACK_ID,
            MARASAI_ID,
        }

    def test_finds_both_lines_a_suit_descends_from(
        self, test_db_session: Session
    ) -> None:
        """The Hi-Zack descends from the Zaku and the GM lines alike."""
        assert walk(test_db_session, ANCESTORS, MARASAI_ID) == {
            HI_ZACK_ID,
            ZAKU_II_ID,
            GM_ID,
        }

    def test_lists_a_shared_descendant_once(self, test_db_session: Session) -> None:
        """A second edge into the same suit must not repeat it."""
        link(MARASAI_ID, MobileSuitRelationType.VARIANT_OF, ZAKU_II_ID)
        test_db_session.commit()

        rows = test_db_session.execute(DESCENDANTS, {"root": ZAKU_II_ID}).all()

        assert sorted(row.mobile_suit_id for row in rows) == sorted(
            [WORKER_ZAKU_ID, HI_ZACK_ID, MARASAI_ID]
        )

    def test_finds_nothing_for_a_suit_with_no_edges(
        self, test_db_session: Session
    ) -> None:
        assert walk(test_db_session, DESCENDANTS, GELGOOG_ID) == set()
        assert walk(test_db_session, ANCESTORS, GELGOOG_ID) == set()

    def test_stops_at_a_cycle_instead_of_looping(
        self, test_db_session: Session
    ) -> None:
        """Bad upstream data can loop; ``CYCLE`` ends the walk there.

        Without it, ``UNION ALL`` would recurse until the statement
        timeout.
        """
        link(ZAKU_II_ID, MobileSuitRelationType.UPGRADE_OF, MARASAI_ID)
        test_db_session.commit()

        assert walk(test_db_session, DESCENDANTS, ZAKU_II_ID) == {
            WORKER_ZAKU_ID,
            HI_ZACK_ID,
            MARASAI_ID,
        }
        assert walk(test_db_session, ANCESTORS, ZAKU_II_ID) == {
            MARASAI_ID,
            HI_ZACK_ID,
            GM_ID,
        }
