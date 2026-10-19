"""The request-scoped database session (FAPI-9)."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from db.db_session_manager import DBSessionManager


def db_session_generator() -> Iterator[Session]:
    """Open a session, roll it back if the route raises, and close it.

    It never commits: code after a dependency's ``yield`` runs after the
    response is sent, so the route commits its own writes (SQLA-15).
    """
    session = DBSessionManager().scoped_session.session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def api_db_session() -> Iterator[Session]:
    """Provide the route's session; tests override this function."""
    yield from db_session_generator()


type DBSessionDep = Annotated[Session, Depends(api_db_session)]
