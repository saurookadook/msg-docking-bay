import logging

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import text
from sqlalchemy.orm import Session

from _factories.mobile_suit.db import MobileSuitDBFactory
from _factories.work.db import WorkDBFactory
from scripts.explain_search import explain, main


@pytest.fixture
def catalog(test_db_session: Session) -> None:
    MobileSuitDBFactory(name="Zaku II", slug="zaku-ii")
    WorkDBFactory(slug="mobile-suit-gundam", title="Mobile Suit Gundam")
    test_db_session.commit()


@pytest.mark.usefixtures("catalog")
class TestExplain:
    def test_plans_every_statement_the_search_sends(
        self, test_db_session: Session
    ) -> None:
        """A page and a count per kind: ten plans, each one executed."""
        plans = explain(test_db_session, "zaku")

        assert len(plans) == 10
        assert all("Execution Time" in query_plan.plan for query_plan in plans)
        assert all(
            query_plan.statement.lstrip().startswith("SELECT") for query_plan in plans
        )

    def test_runs_read_only(
        self, test_db_session: Session, mocker: MockerFixture
    ) -> None:
        """``ANALYZE`` runs each query, so the transaction is read-only.

        The mode is read just before the script rolls back: inside the
        suite's savepoint, the rollback also undoes ``SET TRANSACTION``.
        """
        modes: list[str] = []
        rollback = Session.rollback

        def read_mode_then_roll_back(session: Session) -> None:
            modes.append(
                session.execute(text("SHOW transaction_read_only")).scalar_one()
            )
            rollback(session)

        mocker.patch.object(
            Session, "rollback", autospec=True, side_effect=read_mode_then_roll_back
        )

        explain(test_db_session, "zaku")

        assert modes == ["on"]


@pytest.mark.usefixtures("catalog")
class TestMain:
    def test_logs_the_plans_for_each_term(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO, logger="scripts.explain_search"):
            assert main(["zaku", "rx78"]) == 0

        messages = [record.getMessage() for record in caplog.records]
        assert sum("q='zaku'" in message for message in messages) == 10
        assert sum("q='rx78'" in message for message in messages) == 10
        assert all("Execution Time" in message for message in messages)
