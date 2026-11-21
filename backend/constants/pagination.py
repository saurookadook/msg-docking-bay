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
