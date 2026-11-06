"""Fixed instants that tests compare against (PYTEST-18)."""

from datetime import UTC, datetime
from typing import Final

MOCK_UTCNOW: Final[datetime] = datetime(2026, 4, 20, 11, 15, tzinfo=UTC)
"""The suite's fixed "now". Shared safely: ``datetime`` is immutable."""


def get_mock_utcnow() -> datetime:
    """Return the suite's fixed "now": 2026-04-20T11:15:00Z."""
    return MOCK_UTCNOW
