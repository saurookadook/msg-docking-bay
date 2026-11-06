"""Root fixtures for the ingest suite (PYTEST-9).

The test database setup is the backend's own, loaded from its
``_fixtures`` package, so both suites migrate and roll back the same
way.
"""

from _fixtures.environment import use_test_database

# Set before anything reads the configuration (PYTEST-10).
use_test_database()

# The migration at session start, test_db_session and mock_utcnow.
pytest_plugins = ["_fixtures.db"]
