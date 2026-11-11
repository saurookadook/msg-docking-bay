import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import Table, delete, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_appearance.db import MobileSuitAppearanceDBFactory
from _factories.mobile_suit_organization.db import MobileSuitOrganizationDBFactory
from _factories.organization.db import OrganizationDBFactory
from _factories.organization_appearance.db import OrganizationAppearanceDBFactory
from _factories.source.db import SourceDBFactory
from _factories.work.db import WorkDBFactory
from constants.catalog import MobileSuitOrganizationRole
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.mobile_suit.db import MobileSuitDB
from models.mobile_suit_appearance.db import MobileSuitAppearanceDB
from models.mobile_suit_organization.db import MobileSuitOrganizationDB
from models.organization.db import OrganizationDB
from models.organization_appearance.db import OrganizationAppearanceDB
from models.source.db import SourceDB

ANAHEIM_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1000001")
ZETA_GUNDAM_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1000002")
ZETA_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1000003")
CCA_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1000004")
ZZ_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1000005")
SOURCE_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1000006")
LINK_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1000007")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c10000ff")


@pytest.fixture
def anaheim_and_zeta(test_db_session: Session) -> None:
    """Both appear in Zeta; Anaheim alone in CCA, the suit in ZZ."""
    OrganizationDBFactory(id=ANAHEIM_ID, name="Anaheim Electronics")
    MobileSuitDBFactory(id=ZETA_GUNDAM_ID, name="Zeta Gundam")
    WorkDBFactory(id=ZETA_ID, title="Mobile Suit Zeta Gundam")
    WorkDBFactory(id=CCA_ID, title="Char's Counterattack")
    WorkDBFactory(id=ZZ_ID, title="Mobile Suit Gundam ZZ")
    SourceDBFactory(id=SOURCE_ID)
    test_db_session.flush()
    for work_id in (ZETA_ID, CCA_ID):
        OrganizationAppearanceDBFactory(
            organization_id=ANAHEIM_ID, source_id=SOURCE_ID, work_id=work_id
        )
    for work_id in (ZETA_ID, ZZ_ID):
        MobileSuitAppearanceDBFactory(
            mobile_suit_id=ZETA_GUNDAM_ID, source_id=SOURCE_ID, work_id=work_id
        )
    test_db_session.commit()


def link(**overrides: Any) -> None:
    MobileSuitOrganizationDBFactory(
        **{
            "mobile_suit_id": ZETA_GUNDAM_ID,
            "organization_id": ANAHEIM_ID,
            "role": MobileSuitOrganizationRole.MANUFACTURER,
            "source_id": SOURCE_ID,
            "work_id": ZETA_ID,
            **overrides,
        }
    )


def link_works(test_db_session: Session) -> list[uuid.UUID | None]:
    """Each remaining link's work, nulls last."""
    return list(
        test_db_session.execute(
            text("SELECT work_id FROM mobile_suit_organizations ORDER BY work_id")
        ).scalars()
    )


class TestMobileSuitOrganizationDBTable:
    def test_has_a_surrogate_id_and_no_updated_at(self) -> None:
        """The RDB-2 deviation: a nullable ``work_id`` is not a key."""
        table: Table = BaseDB.metadata.tables["mobile_suit_organizations"]

        assert [c.name for c in table.primary_key] == ["id"]
        assert table.c.work_id.nullable is True
        assert "updated_at" not in table.c


@pytest.mark.usefixtures("anaheim_and_zeta")
class TestMobileSuitOrganizationDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        link(id=LINK_ID)
        test_db_session.commit()
        test_db_session.expunge_all()

        row = test_db_session.execute(select(MobileSuitOrganizationDB)).scalar_one()

        assert row.id == LINK_ID
        assert row.mobile_suit_id == ZETA_GUNDAM_ID
        assert row.organization_id == ANAHEIM_ID
        assert row.role is MobileSuitOrganizationRole.MANUFACTURER
        assert row.source_id == SOURCE_ID
        assert row.work_id == ZETA_ID
        assert row.created_at == mock_utcnow

    def test_stores_the_role_value(self, test_db_session: Session) -> None:
        """The enum type holds values, not member names (SQLA-11)."""
        link()
        test_db_session.flush()

        stored = test_db_session.execute(
            text("SELECT role::text FROM mobile_suit_organizations")
        ).scalar_one()

        assert stored == "manufacturer"

    def test_accepts_a_link_with_no_work(self, test_db_session: Session) -> None:
        """MATCH SIMPLE: a null ``work_id`` needs no appearance."""
        link(work_id=None)

        test_db_session.flush()

    def test_allows_one_organization_in_several_roles(
        self, test_db_session: Session
    ) -> None:
        """Anaheim can build a suit and field it too."""
        link(role=MobileSuitOrganizationRole.MANUFACTURER)
        link(role=MobileSuitOrganizationRole.OPERATOR)

        test_db_session.flush()

    def test_deletes_links_when_an_organization_appearance_is_deleted(
        self, test_db_session: Session
    ) -> None:
        """The no-work row relies on no appearance, so it stays."""
        link(work_id=ZETA_ID)
        link(work_id=None)
        test_db_session.commit()

        test_db_session.execute(
            delete(OrganizationAppearanceDB).where(
                OrganizationAppearanceDB.work_id == ZETA_ID
            )
        )
        test_db_session.commit()

        assert link_works(test_db_session) == [None]

    def test_deletes_links_when_a_suit_appearance_is_deleted(
        self, test_db_session: Session
    ) -> None:
        link(work_id=ZETA_ID)
        link(work_id=None)
        test_db_session.commit()

        test_db_session.execute(
            delete(MobileSuitAppearanceDB).where(
                MobileSuitAppearanceDB.work_id == ZETA_ID
            )
        )
        test_db_session.commit()

        assert link_works(test_db_session) == [None]

    @pytest.mark.parametrize("deleted", [MobileSuitDB, OrganizationDB])
    def test_deletes_every_link_when_the_suit_or_organization_is_deleted(
        self, test_db_session: Session, deleted: type[MobileSuitDB | OrganizationDB]
    ) -> None:
        """The plain FK removes the no-work row too."""
        link(work_id=ZETA_ID)
        link(work_id=None)
        test_db_session.commit()

        deleted_id = ZETA_GUNDAM_ID if deleted is MobileSuitDB else ANAHEIM_ID
        test_db_session.delete(test_db_session.get_one(deleted, deleted_id))
        test_db_session.commit()

        assert link_works(test_db_session) == []


@pytest.mark.usefixtures("anaheim_and_zeta")
class TestMobileSuitOrganizationDBConstraints:
    @pytest.mark.parametrize("work_id", [ZETA_ID, None])
    def test_rejects_a_duplicate_link(
        self, test_db_session: Session, work_id: uuid.UUID | None
    ) -> None:
        """NULLS NOT DISTINCT: one no-work row per suit, org, role."""
        link(work_id=work_id)
        test_db_session.commit()
        link(work_id=work_id)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "mobile_suit_organizations_link_key",
        )

    @pytest.mark.parametrize(
        "work_id, constraint",
        [
            # The Zeta Gundam is not in CCA; Anaheim is not in ZZ.
            (CCA_ID, "mobile_suit_organizations_mobile_suit_id_work_id_fkey"),
            (ZZ_ID, "mobile_suit_organizations_organization_id_work_id_fkey"),
        ],
    )
    def test_rejects_a_work_without_both_appearances(
        self, test_db_session: Session, work_id: uuid.UUID, constraint: str
    ) -> None:
        link(work_id=work_id)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    @pytest.mark.parametrize(
        "column, constraint",
        [
            ("mobile_suit_id", "mobile_suit_organizations_mobile_suit_id_fkey"),
            ("organization_id", "mobile_suit_organizations_organization_id_fkey"),
            ("source_id", "mobile_suit_organizations_source_id_fkey"),
        ],
    )
    def test_rejects_a_missing_reference_with_no_work(
        self, test_db_session: Session, column: str, constraint: str
    ) -> None:
        """The plain FKs check what MATCH SIMPLE skips."""
        link(**{column: MISSING_ID, "work_id": None})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23503", constraint)

    def test_blocks_deleting_a_source_a_link_cites(
        self, test_db_session: Session
    ) -> None:
        """RESTRICT: provenance cannot vanish from under it.

        The appearances cite another source, so the link's RESTRICT is
        checked with no appearance in the way.
        """
        other_source = SourceDBFactory()
        test_db_session.flush()
        link(source_id=other_source.id)
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(SourceDB, other_source.id))
        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        # 23001 is restrict_violation; a missing key is 23503.
        assert violated_constraint(exc_info.value) == (
            "23001",
            "mobile_suit_organizations_source_id_fkey",
        )
