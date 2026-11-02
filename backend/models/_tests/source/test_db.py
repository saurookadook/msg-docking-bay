import uuid
from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from _factories.source.db import SourceDBFactory
from constants.catalog import ContentLicense, SourceKind
from models._tests.integrity import violated_constraint
from models.source.db import SourceDB

RX_78_2_PAGE_ID = uuid.UUID("019a1984-0750-7142-aedd-75291c5b9001")


class TestSourceDB:
    def test_round_trips_every_column(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        retrieved_at = datetime(2025, 8, 26, 0, 0, tzinfo=UTC)
        SourceDBFactory(
            id=RX_78_2_PAGE_ID,
            content_license=ContentLicense.CC_BY_SA_3_0,
            external_id="2167",
            kind=SourceKind.FANDOM_PAGE,
            retrieved_at=retrieved_at,
            revision_id=4_294_967_296,
            url="https://gundam.fandom.com/wiki/RX-78-2_Gundam",
        )
        test_db_session.commit()
        test_db_session.expunge_all()

        source = test_db_session.execute(
            select(SourceDB).where(SourceDB.id == RX_78_2_PAGE_ID)
        ).scalar_one()

        assert source.content_license is ContentLicense.CC_BY_SA_3_0
        assert source.external_id == "2167"
        assert source.kind is SourceKind.FANDOM_PAGE
        assert source.retrieved_at == retrieved_at
        assert source.revision_id == 4_294_967_296  # past 2**31: BIGINT
        assert source.url == "https://gundam.fandom.com/wiki/RX-78-2_Gundam"
        assert source.created_at == mock_utcnow
        assert source.updated_at == mock_utcnow

    def test_stores_the_enum_values_not_the_member_names(
        self, test_db_session: Session
    ) -> None:
        """SQLAlchemy stores enum names by default (SQLA-11)."""
        SourceDBFactory(
            id=RX_78_2_PAGE_ID,
            content_license=ContentLicense.CC0_1_0,
            external_id="Q1134906",
            kind=SourceKind.WIKIDATA_ITEM,
            url="https://www.wikidata.org/wiki/Q1134906",
        )
        test_db_session.commit()

        stored = test_db_session.execute(
            text(
                "SELECT content_license::text, kind::text FROM sources WHERE id = :id"
            ),
            {"id": RX_78_2_PAGE_ID},
        ).one()

        assert tuple(stored) == ("cc0_1_0", "wikidata_item")

    def test_allows_one_external_id_under_different_kinds(
        self, test_db_session: Session
    ) -> None:
        """Page IDs repeat across wikis: the key is ``(kind, id)``."""
        SourceDBFactory(external_id="2167", kind=SourceKind.FANDOM_PAGE)
        SourceDBFactory(
            external_id="2167",
            content_license=ContentLicense.CC_BY_SA_4_0,
            kind=SourceKind.WIKIPEDIA_PAGE,
        )

        test_db_session.flush()


class TestSourceDBConstraints:
    def test_rejects_a_duplicate_page(self, test_db_session: Session) -> None:
        SourceDBFactory(external_id="2167", kind=SourceKind.FANDOM_PAGE)
        SourceDBFactory(external_id="2167", kind=SourceKind.FANDOM_PAGE)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == (
            "23505",
            "sources_kind_external_id_key",
        )

    @pytest.mark.parametrize(
        "overrides, constraint",
        [
            ({"external_id": ""}, "ck_sources_external_id_not_empty"),
            ({"revision_id": 0}, "ck_sources_revision_id_positive"),
            ({"url": "http://gundam.fandom.com/"}, "ck_sources_url_format"),
            ({"url": "gundam.fandom.com/"}, "ck_sources_url_format"),
        ],
    )
    def test_rejects_an_invalid_value(
        self, test_db_session: Session, overrides: dict[str, Any], constraint: str
    ) -> None:
        SourceDBFactory(**overrides)

        with pytest.raises(IntegrityError) as exc_info:
            test_db_session.flush()

        assert violated_constraint(exc_info.value) == ("23514", constraint)
