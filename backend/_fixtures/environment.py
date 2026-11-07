"""Point a test process at the test database (PYTEST-10).

Kept apart from ``_fixtures.db``: a root ``conftest.py`` imports this
module before pytest loads ``_fixtures.db`` as a plugin, and pytest
rewrites a plugin's asserts only if nothing imported it first.
"""

import os
from typing import Final

from config.env_vars import EnvVarManager

TEST_DATABASE_NAME: Final = "test_msg_docking_bay"


def use_test_database() -> None:
    """Point the configuration at the test database.

    Call it at the top of a root ``conftest.py``, before importing a
    module that configures logging or reads settings at import.
    """
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_NAME"] = TEST_DATABASE_NAME
    EnvVarManager().reload()  # the frozen EnvVars is re-validated, never assigned to
