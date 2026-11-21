"""Fixtures for the model and facade tests (PYTEST-9)."""

import pytest
from sqlalchemy.orm import Session

from models._tests.query_count import CountStatements, statement_counter


@pytest.fixture
def count_statements(test_db_session: Session) -> CountStatements:
    """Count the statements sent inside ``with count_statements():``."""
    return statement_counter(test_db_session)
