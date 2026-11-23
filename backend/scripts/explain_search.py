"""Log the query plans of the catalog search (postgresql.md PG-21).

For each term, this runs ``CatalogSearchFacade.search`` as the route
does, records every statement it sends, and runs ``EXPLAIN (ANALYZE,
BUFFERS)`` on each one with the same parameters. The search runs each
list's ``q`` query, so the plans also cover the five list routes. The
default terms are a prefix match (``zaku``) and a mid-word match
(``gundam``), the two shapes D8 ranks.

Everything runs in one read-only transaction that is rolled back.
``ANALYZE`` executes each query, but a search only reads.

Run it wherever the backend's environment is configured:

- local stack: ``docker compose run --rm backend python -m
  scripts.explain_search``;
- Railway: ``railway ssh -s msg-docking-bay-backend -- python -m
  scripts.explain_search``, which runs in the deployed backend
  container, against the hosted database.

Pass terms to explain others: ``python -m scripts.explain_search rx78``.
"""

import argparse
import logging
import sys
from collections.abc import Sequence
from typing import Any, Final, NamedTuple

from sqlalchemy import event, text
from sqlalchemy.orm import Session

from constants.pagination import SEARCH_DEFAULT_LIMIT
from db.db_session_manager import DBSessionManager
from models.search.facade import CatalogSearchFacade
from utils.logging.init import init_logging

DEFAULT_TERMS: Final = ("zaku", "gundam")
DESCRIPTION: Final = "Log EXPLAIN (ANALYZE, BUFFERS) plans for the catalog search."

logger = logging.getLogger(__name__)


class QueryPlan(NamedTuple):
    """One statement the search sent, and its plan."""

    statement: str
    plan: str


def explain(db_session: Session, q: str) -> list[QueryPlan]:
    """Return the plan of every statement one search for ``q`` sends.

    The session's transaction is made read-only first, and rolled back
    at the end, so nothing the plans execute is kept.
    """
    db_session.execute(text("SET TRANSACTION READ ONLY"))
    connection = db_session.connection()
    sent: list[tuple[str, Any]] = []

    def record(
        _conn: object,
        _cursor: object,
        statement: str,
        # The driver's own parameter shape, passed back to it unchanged.
        parameters: Any,  # noqa: ANN401
        _context: object,
        _executemany: bool,
    ) -> None:
        sent.append((statement, parameters))

    event.listen(connection, "before_cursor_execute", record)
    try:
        CatalogSearchFacade(db_session=db_session).search(
            q=q, limit=SEARCH_DEFAULT_LIMIT
        )
    finally:
        event.remove(connection, "before_cursor_execute", record)

    try:
        return [
            QueryPlan(
                statement=statement,
                plan="\n".join(
                    row[0]
                    for row in connection.exec_driver_sql(
                        f"EXPLAIN (ANALYZE, BUFFERS) {statement}", parameters
                    )
                ),
            )
            for statement, parameters in sent
        ]
    finally:
        db_session.rollback()


def main(argv: Sequence[str] | None = None) -> int:
    """Log the plans for each term against the configured database."""
    init_logging(app_name="explain-search")
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "terms",
        nargs="*",
        default=list(DEFAULT_TERMS),
        help="the q values to search for (default: zaku gundam)",
    )
    args = parser.parse_args(argv)

    scoped_session = DBSessionManager().scoped_session
    try:
        for term in args.terms:
            plans = explain(scoped_session(), term)
            for number, query_plan in enumerate(plans, start=1):
                logger.info(
                    "q='%s', statement %d of %d:\n%s\n%s",
                    term,
                    number,
                    len(plans),
                    query_plan.statement,
                    query_plan.plan,
                )
    finally:
        scoped_session.remove()
    return 0


if __name__ == "__main__":
    sys.exit(main())
