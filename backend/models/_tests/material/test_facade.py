from datetime import datetime

from sqlalchemy.orm import Session

from models.material.facade import MaterialFacade


class TestMaterialFacadeCreateOrUpdate:
    def test_create_or_update_leaves_an_unchanged_row_alone(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """A rerun keeps ``updated_at`` (SQLA-25)."""
        facade = MaterialFacade(db_session=test_db_session)
        payload = {
            "fandom_page_id": 3877,
            "fandom_page_title": "Luna Titanium Alloy",
            "name": "Luna Titanium Alloy",
            "slug": "luna-titanium-alloy",
        }

        created = facade.create_or_update(payload=payload)
        rerun = facade.create_or_update(payload=payload)

        assert created.fandom_page_id == 3877
        assert created.updated_at != mock_utcnow
        assert (rerun.id, rerun.updated_at) == (created.id, created.updated_at)

    def test_create_or_update_renames_on_the_slug(
        self, test_db_session: Session
    ) -> None:
        facade = MaterialFacade(db_session=test_db_session)
        payload = {"name": "Luna Titanium Alloy", "slug": "luna-titanium-alloy"}

        created = facade.create_or_update(payload=payload)
        renamed = facade.create_or_update(payload={**payload, "name": "Renamed"})

        assert (renamed.id, renamed.name) == (created.id, "Renamed")
