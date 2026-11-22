import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from _factories.mechanical_designer_slug_redirect.db import (
    MechanicalDesignerSlugRedirectDBFactory,
)
from models._tests.integrity import violated_constraint
from models.mechanical_designer.db import MechanicalDesignerDB
from models.mechanical_designer_slug_redirect.db import MechanicalDesignerSlugRedirectDB

ENTITY_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc001")
MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5bc0ff")


class TestMechanicalDesignerSlugRedirectDB:
    def test_has_the_old_slug_as_its_primary_key_and_no_surrogate_id(self) -> None:
        table = MechanicalDesignerSlugRedirectDB.__table__

        assert [column.name for column in table.primary_key] == ["old_slug"]
        assert "id" not in table.c

    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        MechanicalDesignerDBFactory(id=ENTITY_ID, slug="kunio-okawara")
        MechanicalDesignerSlugRedirectDBFactory(
            mechanical_designer_id=ENTITY_ID, old_slug="okawara"
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        redirect = test_db_session.execute(
            select(MechanicalDesignerSlugRedirectDB)
        ).scalar_one()

        assert redirect.mechanical_designer_id == ENTITY_ID
        assert redirect.old_slug == "okawara"
        assert redirect.created_at == mock_utcnow

    def test_deletes_the_redirect_when_the_designer_is_deleted(
        self, test_db_session: Session
    ) -> None:
        MechanicalDesignerDBFactory(id=ENTITY_ID)
        MechanicalDesignerSlugRedirectDBFactory(mechanical_designer_id=ENTITY_ID)
        test_db_session.commit()

        test_db_session.delete(test_db_session.get_one(MechanicalDesignerDB, ENTITY_ID))
        test_db_session.commit()

        assert (
            test_db_session.scalars(select(MechanicalDesignerSlugRedirectDB)).all()
            == []
        )

    def test_rejects_a_malformed_old_slug(self, test_db_session: Session) -> None:
        MechanicalDesignerDBFactory(id=ENTITY_ID)
        MechanicalDesignerSlugRedirectDBFactory(
            mechanical_designer_id=ENTITY_ID, old_slug="Okawara_K"
        )

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23514",
            "ck_mechanical_designer_slug_redirects_old_slug_format",
        )

    def test_rejects_a_missing_designer(self, test_db_session: Session) -> None:
        MechanicalDesignerSlugRedirectDBFactory(mechanical_designer_id=MISSING_ID)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23503",
            "mechanical_designer_slug_redirects_mechanical_designer_id_fkey",
        )
