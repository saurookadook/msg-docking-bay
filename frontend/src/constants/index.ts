/**
 * @description Base URL that `safeFetch` resolves `/api/...` paths against.
 * @note Empty on purpose: the browser calls the API on its own origin, and the reverse
 * proxy routes `/api` to the backend (ENV-40), so no API host is baked into the build.
 */
export const BASE_API_URL = '';
