from datetime import datetime

from sqlalchemy.orm import Session

from models.armament.facade import ArmamentFacade


class TestArmamentFacadeCreateOrUpdate:
    def test_create_or_update_leaves_an_unchanged_row_alone(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """A rerun keeps ``updated_at`` (SQLA-25)."""
        facade = ArmamentFacade(db_session=test_db_session)
        payload = {
            "fandom_page_id": 3606,
            "fandom_page_title": "Vulcan Gun",
            "name": "Vulcan Gun",
            "slug": "vulcan-gun",
        }

        created = facade.create_or_update(payload=payload)
        rerun = facade.create_or_update(payload=payload)

        assert created.fandom_page_id == 3606
        assert created.updated_at != mock_utcnow
        assert (rerun.id, rerun.updated_at) == (created.id, created.updated_at)

    def test_create_or_update_renames_on_the_slug(
        self, test_db_session: Session
    ) -> None:
        facade = ArmamentFacade(db_session=test_db_session)
        payload = {"name": "Vulcan Gun", "slug": "vulcan-gun"}

        created = facade.create_or_update(payload=payload)
        renamed = facade.create_or_update(payload={**payload, "name": "Renamed"})

        assert (renamed.id, renamed.name) == (created.id, "Renamed")
