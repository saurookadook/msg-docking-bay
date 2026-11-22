from datetime import datetime

from sqlalchemy.orm import Session

from models.powerplant.facade import PowerplantFacade


class TestPowerplantFacadeCreateOrUpdate:
    def test_inserts_then_leaves_an_unchanged_row_alone(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """A rerun keeps ``updated_at`` (SQLA-25)."""
        facade = PowerplantFacade(db_session=test_db_session)
        payload = {
            "fandom_page_id": None,
            "fandom_page_title": None,
            "name": "Minovsky Ultracompact Fusion Reactor",
            "slug": "minovsky-ultracompact-fusion-reactor",
        }

        created = facade.create_or_update(payload=payload)
        rerun = facade.create_or_update(payload=payload)

        assert created.fandom_page_id is None
        assert created.updated_at != mock_utcnow
        assert (rerun.id, rerun.updated_at) == (created.id, created.updated_at)

    def test_updates_on_the_slug(self, test_db_session: Session) -> None:
        facade = PowerplantFacade(db_session=test_db_session)
        payload = {
            "name": "Minovsky Ultracompact Fusion Reactor",
            "slug": "minovsky-ultracompact-fusion-reactor",
        }

        created = facade.create_or_update(payload=payload)
        renamed = facade.create_or_update(payload={**payload, "name": "Renamed"})

        assert (renamed.id, renamed.name) == (created.id, "Renamed")
