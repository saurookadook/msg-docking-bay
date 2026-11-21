"""Count the statements a block of code sends (pytest.md PYTEST-24)."""

from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass

from sqlalchemy import event
from sqlalchemy.orm import Session


@dataclass
class StatementCount:
    """How many statements reached the database inside the block."""

    value: int = 0


type CountStatements = Callable[[], AbstractContextManager[StatementCount]]


def statement_counter(db_session: Session) -> CountStatements:
    """Build a context manager that counts the session's statements.

    It listens for ``before_cursor_execute`` on the session's
    connection, so every statement is counted, eager loads included.
    """

    @contextmanager
    def count_statements() -> Generator[StatementCount]:
        connection = db_session.connection()
        count = StatementCount()

        def on_execute(*_args: object) -> None:
            count.value += 1

        event.listen(connection, "before_cursor_execute", on_execute)
        try:
            yield count
        finally:
            event.remove(connection, "before_cursor_execute", on_execute)

    return count_statements
