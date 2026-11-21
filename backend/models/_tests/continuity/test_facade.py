import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from models.continuity.db import ContinuityDB
from models.continuity.entity import ContinuityCardEntity
from models.continuity.facade import ContinuityFacade

UC_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bd001")


class TestContinuityFacade:
    def test_get_all(self, test_db_session: Session, mock_utcnow: datetime) -> None:
        ContinuityDBFactory(
            id=UC_ID, name="Universal Century", slug="universal-century"
        )
        ContinuityDBFactory(
            name="Universal Century (GQ)",
            parent_continuity_id=UC_ID,
            slug="universal-century-gq",
        )
        ContinuityDBFactory(name="Cosmic Era", slug="cosmic-era")
        test_db_session.commit()

        continuities = ContinuityFacade(db_session=test_db_session).get_all()

        assert [c.model_dump() for c in continuities] == [
            {
                "created_at": mock_utcnow,
                "name": "Cosmic Era",
                "parent_continuity": None,
                "slug": "cosmic-era",
                "updated_at": mock_utcnow,
            },
            {
                "created_at": mock_utcnow,
                "name": "Universal Century",
                "parent_continuity": None,
                "slug": "universal-century",
                "updated_at": mock_utcnow,
            },
            {
                "created_at": mock_utcnow,
                "name": "Universal Century (GQ)",
                "parent_continuity": {
                    "name": "Universal Century",
                    "slug": "universal-century",
                },
                "slug": "universal-century-gq",
                "updated_at": mock_utcnow,
            },
        ]

    def test_get_all_empty(self, test_db_session: Session) -> None:
        assert ContinuityFacade(db_session=test_db_session).get_all() == []

    def test_create_or_update(self, test_db_session: Session) -> None:
        facade = ContinuityFacade(db_session=test_db_session)

        created = facade.create_or_update(
            payload={"name": "Cosmic Era", "slug": "cosmic-era"}
        )
        rerun = facade.create_or_update(
            payload={"name": "Cosmic Era", "slug": "cosmic-era"}
        )

        assert rerun == created


class TestContinuityCardEntity:
    def test_fails_on_a_row_whose_parent_was_not_loaded(
        self, test_db_session: Session
    ) -> None:
        """Relationships are lazy="raise": a missing load fails."""
        ContinuityDBFactory(slug="cosmic-era")
        test_db_session.commit()
        test_db_session.expunge_all()
        row = test_db_session.scalars(select(ContinuityDB)).one()

        with pytest.raises(ValidationError, match="get_attribute_error"):
            ContinuityCardEntity.model_validate(row)
