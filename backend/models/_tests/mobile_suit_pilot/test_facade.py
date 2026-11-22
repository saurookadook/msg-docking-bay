import uuid

from sqlalchemy.orm import Session

from _factories.character.db import CharacterDBFactory
from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.mobile_suit_pilot.db import MobileSuitPilotDBFactory
from _factories.source.db import SourceDBFactory
from models.mobile_suit_pilot.facade import MobileSuitPilotFacade

MISSING_ID = uuid.UUID("019a1984-0750-7142-aedd-7529c1f000ff")


class TestMobileSuitPilotFacadeReads:
    def test_get_for_suit_with_no_pilots(self, test_db_session: Session) -> None:
        """An unknown suit has no pilots; the caller owns the 404."""
        assert (
            MobileSuitPilotFacade(db_session=test_db_session).get_for_suit(MISSING_ID)
            == []
        )

    def test_get_for_character_with_no_suits(self, test_db_session: Session) -> None:
        assert (
            MobileSuitPilotFacade(db_session=test_db_session).get_for_character(
                MISSING_ID
            )
            == []
        )

    def test_reads_both_ways(self, test_db_session: Session) -> None:
        amuro = CharacterDBFactory(name="Amuro Ray", slug="amuro-ray")
        rx_78_2_gundam = MobileSuitDBFactory(slug="rx-78-2-gundam")
        source = SourceDBFactory()
        test_db_session.flush()
        MobileSuitPilotDBFactory(
            character_id=amuro.id,
            mobile_suit_id=rx_78_2_gundam.id,
            source_id=source.id,
            work_id=None,
        )
        test_db_session.commit()
        facade = MobileSuitPilotFacade(db_session=test_db_session)

        [credit] = facade.get_for_suit(rx_78_2_gundam.id)
        [piloted] = facade.get_for_character(amuro.id)

        assert (credit.character.slug, credit.work) == ("amuro-ray", None)
        assert (piloted.mobile_suit.slug, piloted.work) == ("rx-78-2-gundam", None)


class TestMobileSuitPilotFacadeCreateOrUpdate:
    def test_with_no_work(self, test_db_session: Session) -> None:
        """A rerun finds the null-work pairing, not a second one."""
        amuro = CharacterDBFactory()
        rx_78_2_gundam = MobileSuitDBFactory()
        source, new_source = SourceDBFactory(), SourceDBFactory()
        test_db_session.commit()
        facade = MobileSuitPilotFacade(db_session=test_db_session)
        payload = {
            "character_id": amuro.id,
            "mobile_suit_id": rx_78_2_gundam.id,
            "source_id": source.id,
            "work_id": None,
        }

        first = facade.create_or_update(payload=payload)
        rerun = facade.create_or_update(payload={**payload, "source_id": new_source.id})

        assert rerun.id == first.id
        assert rerun.source_id == new_source.id
