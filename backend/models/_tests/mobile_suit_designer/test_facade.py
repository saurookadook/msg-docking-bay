import uuid

from sqlalchemy.orm import Session

from _factories.mechanical_designer.db import MechanicalDesignerDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.source.db import SourceDBFactory
from models.mobile_suit_designer.facade import MobileSuitDesignerFacade

MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c3f000ff")


class TestMobileSuitDesignerFacadeReads:
    def test_get_for_suit_with_no_designers(self, test_db_session: Session) -> None:
        """An unknown suit has no designers; the caller owns the 404."""
        assert (
            MobileSuitDesignerFacade(db_session=test_db_session).get_for_suit(
                MISSING_ID
            )
            == []
        )


class TestMobileSuitDesignerFacadeCreateOrUpdate:
    def test_updates_the_source(self, test_db_session: Session) -> None:
        okawara = MechanicalDesignerDBFactory()
        rx_78_2_gundam = MobileSuitDBFactory()
        source, new_source = SourceDBFactory(), SourceDBFactory()
        test_db_session.commit()
        facade = MobileSuitDesignerFacade(db_session=test_db_session)
        payload = {
            "mechanical_designer_id": okawara.id,
            "mobile_suit_id": rx_78_2_gundam.id,
            "source_id": source.id,
        }

        facade.create_or_update(payload=payload)
        credit = facade.create_or_update(
            payload={**payload, "source_id": new_source.id}
        )

        assert credit.source_id == new_source.id
