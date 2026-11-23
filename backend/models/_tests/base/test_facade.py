from collections.abc import Mapping
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from _factories.continuity.db import ContinuityDBFactory
from db.db_session_manager import DBSessionManager
from models._tests.query_count import CountStatements
from models.base.facade import BaseFacade, normalize_search
from models.continuity.db import ContinuityDB


class ContinuityProbeFacade(BaseFacade):
    """Reach the protected helpers the way a real facade does."""

    def search_names(self, q: str) -> list[str] | None:
        """Names matching ``q``, or ``None`` when ``q`` is no filter."""
        search = self._search_clauses(q, [ContinuityDB.slug])
        if search is None:
            return None
        return list(
            self.db_session.scalars(
                select(ContinuityDB.name)
                .where(search.filter)
                .order_by(search.rank, ContinuityDB.name)
            ).all()
        )

    def upsert(self, payload: Mapping[str, Any]) -> ContinuityDB:
        return self._upsert(ContinuityDB, payload=payload, conflict_columns=["slug"])


class TestNormalizeSearch:
    @pytest.mark.parametrize(
        ("q", "needle"),
        [
            ("RX-78-2", "rx782"),
            ("RX 78-2", "rx782"),
            ("rx782", "rx782"),
            ("Turn A", "turna"),
            ("∀", None),
            (" -- ", None),
            ("%_", None),
            ("", None),
            (None, None),
        ],
    )
    def test_keeps_only_lowercase_letters_and_digits(
        self, q: str | None, needle: str | None
    ) -> None:
        assert normalize_search(q) == needle


class TestBaseFacade:
    def test_uses_the_session_it_is_given(self, test_db_session: Session) -> None:
        assert BaseFacade(db_session=test_db_session).db_session is test_db_session

    def test_falls_back_to_the_scoped_session(self) -> None:
        """For scripts: the test fixture binds that same registry."""
        scoped_session = DBSessionManager().scoped_session()

        assert BaseFacade().db_session is scoped_session

    def test_search_clauses_match_normalized_columns_prefix_first(
        self, test_db_session: Session
    ) -> None:
        ContinuityDBFactory(name="After Colony", slug="after-colony")
        ContinuityDBFactory(name="Cosmic Era", slug="cosmic-era")
        ContinuityDBFactory(name="Era of Sail", slug="era-of-sail")
        test_db_session.commit()
        facade = ContinuityProbeFacade(db_session=test_db_session)

        names = facade.search_names("ERA")

        assert names == ["Era of Sail", "Cosmic Era"]

    @pytest.mark.parametrize("q", [" -- ", "%_", "∀"])
    def test_search_clauses_blank_q_is_no_filter(
        self, test_db_session: Session, q: str
    ) -> None:
        facade = ContinuityProbeFacade(db_session=test_db_session)

        assert facade.search_names(q) is None


class TestUpsert:
    def test_inserts_a_new_row(self, test_db_session: Session) -> None:
        facade = ContinuityProbeFacade(db_session=test_db_session)

        row = facade.upsert({"name": "Cosmic Era", "slug": "cosmic-era"})

        assert row.id.version == 7
        assert row.name == "Cosmic Era"

    def test_updates_a_changed_row_and_its_updated_at(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        existing = ContinuityDBFactory(name="Cosmic Era", slug="cosmic-era")
        test_db_session.commit()
        facade = ContinuityProbeFacade(db_session=test_db_session)

        row = facade.upsert({"name": "Cosmic Era (SEED)", "slug": "cosmic-era"})

        assert row.id == existing.id
        assert row.name == "Cosmic Era (SEED)"
        assert row.updated_at != mock_utcnow
        assert row.created_at == mock_utcnow

    def test_leaves_an_unchanged_row_and_its_updated_at_alone(
        self, test_db_session: Session, mock_utcnow: datetime
    ) -> None:
        """A rerun must not make every row look freshly updated (D5)."""
        existing = ContinuityDBFactory(name="Cosmic Era", slug="cosmic-era")
        test_db_session.commit()
        facade = ContinuityProbeFacade(db_session=test_db_session)

        row = facade.upsert({"name": "Cosmic Era", "slug": "cosmic-era"})

        assert row.id == existing.id
        assert row.updated_at == mock_utcnow

    def test_rejects_a_key_that_is_not_a_column(self, test_db_session: Session) -> None:
        facade = ContinuityProbeFacade(db_session=test_db_session)

        with pytest.raises(ValueError, match="Not columns of continuities: tags"):
            facade.upsert({"name": "Cosmic Era", "slug": "cosmic-era", "tags": []})

    def test_rejects_a_payload_of_only_its_key(self, test_db_session: Session) -> None:
        facade = ContinuityProbeFacade(db_session=test_db_session)

        with pytest.raises(ValueError, match="outside its key"):
            facade.upsert({"slug": "cosmic-era"})


class TestCountStatements:
    def test_counts_each_statement_in_the_block(
        self, test_db_session: Session, count_statements: CountStatements
    ) -> None:
        with count_statements() as count:
            test_db_session.execute(text("SELECT 1"))
            test_db_session.execute(text("SELECT 2"))

        assert count.value == 2
