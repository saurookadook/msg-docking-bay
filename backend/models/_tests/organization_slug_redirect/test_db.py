import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.organization.db import OrganizationDBFactory
from _factories.organization_slug_redirect.db import OrganizationSlugRedirectDBFactory
from models._tests.integrity import violated_constraint
from models.organization.db import OrganizationDB
from models.organization_slug_redirect.db import OrganizationSlugRedirectDB

ENTITY_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc001")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc0ff")


class TestOrganizationSlugRedirectDB:
    def test_has_the_old_slug_as_its_primary_key_and_no_surrogate_id(self) -> None:
        table = OrganizationSlugRedirectDB.__table__

        assert [column.name for column in table.primary_key] == ["old_slug"]
        assert "id" not in table.c

    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        OrganizationDBFactory(id=ENTITY_ID, slug="earth-federation")
        OrganizationSlugRedirectDBFactory(organization_id=ENTITY_ID, old_slug="efsf")
        test_db_session.commit()
        test_db_session.expunge_all()

        redirect = test_db_session.execute(
            select(OrganizationSlugRedirectDB)
        ).scalar_one()

        assert redirect.organization_id == ENTITY_ID
        assert redirect.old_slug == "efsf"
        assert redirect.created_at == mock_utcnow

    def test_deletes_the_redirect_when_the_organization_is_deleted(
        self, test_db_session: Session
    ) -> None:
        OrganizationDBFactory(id=ENTITY_ID)
        OrganizationSlugRedirectDBFactory(organization_id=ENTITY_ID)
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(OrganizationDB, ENTITY_ID))
        test_db_session.commit()

        assert test_db_session.scalars(select(OrganizationSlugRedirectDB)).all() == []

    def test_rejects_a_malformed_old_slug(self, test_db_session: Session) -> None:
        OrganizationDBFactory(id=ENTITY_ID)
        OrganizationSlugRedirectDBFactory(organization_id=ENTITY_ID, old_slug="EFSF")

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_organization_slug_redirects_old_slug_format",
        )

    def test_rejects_a_missing_organization(self, test_db_session: Session) -> None:
        OrganizationSlugRedirectDBFactory(organization_id=MISSING_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "organization_slug_redirects_organization_id_fkey",
        )
