/**
 * @description Base URL that `safeFetch` resolves `/api/...` paths against.
 * @note Empty on purpose: the browser calls the API on its own origin, and the reverse
 * proxy routes `/api` to the backend (ENV-40), so no API host is baked into the build.
 */
export const BASE_API_URL = '';

/**
 * @description The `limit` a list route uses when a request gives none.
 * @note Mirrors `DEFAULT_PAGE_SIZE` in `backend/constants/pagination.py`; change both.
 */
export const DEFAULT_PAGE_SIZE = 50;

/**
 * @description The largest `limit` a list route accepts; a larger one is a 422.
 * @note Mirrors `MAX_PAGE_SIZE` in `backend/constants/pagination.py`; change both.
 */
export const MAX_PAGE_SIZE = 100;

/**
 * @description The longest `q` a search accepts; a longer one is a 422.
 * @note Mirrors `MAX_SEARCH_LENGTH` in `backend/constants/pagination.py`; change both.
 */
export const MAX_SEARCH_LENGTH = 100;

/**
 * @description The per-kind `limit` the catalog search uses when a request gives none.
 * @note Mirrors `SEARCH_DEFAULT_LIMIT` in `backend/constants/pagination.py`; change both.
 */
export const SEARCH_DEFAULT_LIMIT = 5;

/**
 * @description The largest per-kind `limit` the catalog search accepts.
 * @note Mirrors `SEARCH_MAX_LIMIT` in `backend/constants/pagination.py`; change both.
 */
export const SEARCH_MAX_LIMIT = 20;
