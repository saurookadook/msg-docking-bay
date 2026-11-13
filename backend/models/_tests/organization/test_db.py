import uuid
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.organization.db import OrganizationDBFactory
from db.base_db import BaseDB
from models._tests.integrity import violated_constraint
from models.organization.db import OrganizationDB

EFF_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0b00001")
TITANS_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c0b00002")


class TestOrganizationDBTable:
    def test_is_named_organizations(self) -> None:
        """The derived name must be the plural the schema uses."""
        assert OrganizationDB.__table__ is BaseDB.metadata.tables["organizations"]


class TestOrganizationDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        OrganizationDBFactory(id=EFF_ID, name="Earth Federation Forces")
        OrganizationDBFactory(
            id=TITANS_ID,
            fandom_page_title="Titans",
            name="Titans",
            parent_organization_id=EFF_ID,
            slug="titans",
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        titans = test_db_session.execute(
            select(OrganizationDB).where(OrganizationDB.id == TITANS_ID)
        ).scalar_one()

        assert titans.fandom_page_title == "Titans"
        assert titans.name == "Titans"
        assert titans.parent_organization_id == EFF_ID
        assert titans.slug == "titans"
        assert titans.created_at == mock_utcnow
        assert titans.updated_at == mock_utcnow

    def test_generates_a_uuidv7_id_on_the_server(
        self, test_db_session: Session
    ) -> None:
        organization = OrganizationDB(name="AEUG", slug="aeug")
        test_db_session.add(organization)
        test_db_session.flush()

        assert organization.id.version == 7

    def test_allows_two_with_the_same_name(self, test_db_session: Session) -> None:
        """Namesakes are told apart by slug."""
        OrganizationDBFactory(name="Neo Zeon")
        OrganizationDBFactory(name="Neo Zeon")

        test_db_session.flush()

    def test_clears_the_parent_link_when_the_parent_is_deleted(
        self, test_db_session: Session
    ) -> None:
        """ON DELETE SET NULL: a unit outlives its parent."""
        eff = OrganizationDBFactory(id=EFF_ID)
        OrganizationDBFactory(id=TITANS_ID, parent_organization_id=EFF_ID)
        test_db_session.commit()

        test_db_session.delete(eff)
        test_db_session.commit()
        test_db_session.expunge_all()

        titans = test_db_session.get_one(OrganizationDB, TITANS_ID)
        assert titans.parent_organization_id is None


class TestOrganizationDBConstraints:
    @pytest.mark.parametrize(
        "column, value, constraint",
        [
            ("fandom_page_title", "Titans", "organizations_fandom_page_title_key"),
            ("slug", "titans", "organizations_slug_key"),
        ],
    )
    def test_rejects_a_duplicate(
        self, test_db_session: Session, column: str, value: str, constraint: str
    ) -> None:
        OrganizationDBFactory(**{column: value})
        OrganizationDBFactory(**{column: value})

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23505", constraint)

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"fandom_page_title": ""}, "ck_organizations_fandom_page_title_not_empty"),
            ({"name": ""}, "ck_organizations_name_not_empty"),
            ({"slug": "Earth_Federation"}, "ck_organizations_slug_format"),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        OrganizationDBFactory(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)

    def test_rejects_an_organization_that_is_its_own_parent(
        self, test_db_session: Session
    ) -> None:
        OrganizationDBFactory(id=EFF_ID, parent_organization_id=EFF_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_organizations_not_own_parent",
        )

    def test_rejects_a_missing_parent(self, test_db_session: Session) -> None:
        OrganizationDBFactory(
            parent_organization_id=uuid.UUID("019a1984-0750-7142-aedd-7529c0b000ff")
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "organizations_parent_organization_id_fkey",
        )
