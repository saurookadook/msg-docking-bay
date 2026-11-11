"""Walk sub-units over ``organizations`` with ``WITH RECURSIVE``.

These prove the parent-link design (RDB-7): a hierarchy comes from a
recursive query, and the ``CYCLE`` clause stops a walk that loops.
The queries live here until Phase 3a moves them into the organization
facade.
"""

import uuid
from typing import Final

import pytest
from sqlalchemy import TextClause, text, update
from sqlalchemy.orm import Session

from _factories.organization.db import OrganizationDBFactory
from models.organization.db import OrganizationDB

EFF_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0b0a001")
EFSF_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0b0a002")
TITANS_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0b0a003")
T3_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0b0a004")
ZEON_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0b0a005")

# Two fixed statements rather than one built per direction: SQL is
# never assembled from strings (SQLA-24).
SUB_UNITS: Final[TextClause] = text(
    """
    WITH RECURSIVE units (organization_id) AS (
        SELECT CAST(:root AS uuid)
        UNION ALL
        SELECT o.id
        FROM units u
        JOIN organizations o ON o.parent_organization_id = u.organization_id
    ) CYCLE organization_id SET is_cycle USING path
    SELECT DISTINCT organization_id FROM units
    WHERE NOT is_cycle AND organization_id <> CAST(:root AS uuid)
    """
)
PARENTS: Final[TextClause] = text(
    """
    WITH RECURSIVE units (organization_id) AS (
        SELECT CAST(:root AS uuid)
        UNION ALL
        SELECT o.parent_organization_id
        FROM units u
        JOIN organizations o ON o.id = u.organization_id
        WHERE o.parent_organization_id IS NOT NULL
    ) CYCLE organization_id SET is_cycle USING path
    SELECT DISTINCT organization_id FROM units
    WHERE NOT is_cycle AND organization_id <> CAST(:root AS uuid)
    """
)


def walk(
    test_db_session: Session, query: TextClause, root: uuid.UUID
) -> set[uuid.UUID]:
    return set(test_db_session.execute(query, {"root": root}).scalars())


@pytest.fixture
def federation_and_zeon(test_db_session: Session) -> None:
    """Build the Federation's units two levels deep, plus an outsider.

    Titans Test Team → Titans → Earth Federation Forces, and Earth
    Federation Space Force → Earth Federation Forces. The Principality
    of Zeon stands alone.
    """
    OrganizationDBFactory(id=EFF_ID, name="Earth Federation Forces")
    OrganizationDBFactory(id=ZEON_ID, name="Principality of Zeon")
    test_db_session.flush()
    OrganizationDBFactory(
        id=EFSF_ID, name="Earth Federation Space Force", parent_organization_id=EFF_ID
    )
    OrganizationDBFactory(id=TITANS_ID, name="Titans", parent_organization_id=EFF_ID)
    test_db_session.flush()
    OrganizationDBFactory(
        id=T3_ID, name="Titans Test Team", parent_organization_id=TITANS_ID
    )
    test_db_session.commit()


@pytest.mark.usefixtures("federation_and_zeon")
class TestOrganizationHierarchy:
    def test_finds_every_sub_unit_through_several_levels(
        self, test_db_session: Session
    ) -> None:
        assert walk(test_db_session, SUB_UNITS, EFF_ID) == {
            EFSF_ID,
            TITANS_ID,
            T3_ID,
        }

    def test_finds_every_parent_up_to_the_top(self, test_db_session: Session) -> None:
        assert walk(test_db_session, PARENTS, T3_ID) == {TITANS_ID, EFF_ID}

    def test_finds_nothing_for_an_organization_with_no_units_or_parent(
        self, test_db_session: Session
    ) -> None:
        assert walk(test_db_session, SUB_UNITS, ZEON_ID) == set()
        assert walk(test_db_session, PARENTS, ZEON_ID) == set()

    def test_stops_at_a_two_organization_cycle_instead_of_looping(
        self, test_db_session: Session
    ) -> None:
        """Bad upstream data can loop; ``CYCLE`` ends the walk there.

        The ``not_own_parent`` check stops only a one-row loop. Without
        ``CYCLE``, ``UNION ALL`` would recurse until the statement
        timeout.
        """
        test_db_session.execute(
            update(OrganizationDB)
            .where(OrganizationDB.id == EFF_ID)
            .values(parent_organization_id=TITANS_ID)
        )
        test_db_session.commit()

        assert walk(test_db_session, SUB_UNITS, TITANS_ID) == {T3_ID, EFF_ID, EFSF_ID}
        assert walk(test_db_session, PARENTS, TITANS_ID) == {EFF_ID}
