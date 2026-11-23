"""Page sizes and search limits for paginated lists (D3, RDB-23)."""

from typing import Final

DEFAULT_PAGE_SIZE: Final = 50
"""The ``limit`` a list uses when the request gives none."""

MAX_PAGE_SIZE: Final = 100
"""The largest ``limit`` a list accepts; a larger one is a 422.

The frontend's Mirage ``paginate()`` mirrors both values.
"""

MAX_SEARCH_LENGTH: Final = 100
"""The longest ``q`` a list accepts; a longer one is a 422 (D8)."""

SEARCH_DEFAULT_LIMIT: Final = 5
"""The per-kind ``limit`` the catalog search uses when given none."""

SEARCH_MAX_LIMIT: Final = 20
"""The largest per-kind ``limit`` the search accepts; more is a 422.

Deeper results page through each kind's own list, with the same ``q``.
"""
