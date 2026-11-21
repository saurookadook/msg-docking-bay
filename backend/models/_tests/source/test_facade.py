from datetime import datetime

from sqlalchemy.orm import Session

from _factories.source.db import SourceDBFactory
from constants.catalog import ContentLicense, SourceKind
from models.source.facade import SourceFacade


class TestSourceFacade:
    def test_create_or_update(self, test_db_session: Session) -> None:
        payload = {
            "content_license": ContentLicense.CC_BY_SA_3_0,
            "external_id": "2034",
            "kind": SourceKind.FANDOM_PAGE,
            "retrieved_at": datetime.fromisoformat("2026-11-15T23:32:58Z"),
            "revision_id": 706484,
            "url": "https://gundam.fandom.com/wiki/RX-78-2_Gundam",
        }

        source = SourceFacade(db_session=test_db_session).create_or_update(
            payload=payload
        )

        assert source.external_id == "2034"
        assert source.revision_id == 706484

    def test_create_or_update_updates_in_place_on_kind_and_external_id(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        existing = SourceDBFactory(external_id="2034", revision_id=700000)
        test_db_session.commit()

        source = SourceFacade(db_session=test_db_session).create_or_update(
            payload={
                "external_id": "2034",
                "kind": SourceKind.FANDOM_PAGE,
                "content_license": existing.content_license,
                "retrieved_at": existing.retrieved_at,
                "revision_id": 706484,
                "url": existing.url,
            }
        )

        assert source.id == existing.id
        assert source.revision_id == 706484
        assert source.updated_at != mock_utcnow
