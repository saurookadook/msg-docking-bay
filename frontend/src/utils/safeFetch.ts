import { BASE_API_URL } from '@/constants';

import { sharedLog } from './logger';
import { safeParseJSON } from './safeParseJSON';

const logger = sharedLog.getLogger('safeFetch');

/**
 * @description The error `safeFetch` throws for a non-2xx response. It keeps the status
 * and the API's `detail` (FAPI-13; a list of errors for a 422, FAPI-23), so callers can
 * show the message the backend wrote for the client.
 */
export class SafeFetchError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor({
    callerName, // force formatting
    detail,
    requestURL,
    status,
  }: {
    callerName: string;
    detail: unknown;
    requestURL: string;
    status: number;
  }) {
    super(
      `[${callerName}] : Request to '${requestURL}' failed with status '${status}'`,
    );
    this.name = 'SafeFetchError';
    this.status = status;
    this.detail = detail;
  }
}

function extractDetail(body: unknown): unknown {
  if (typeof body === 'object' && body != null && 'detail' in body) {
    return body.detail;
  }
  return null;
}

/**
 * @description Calls `fetch` for a path under `/api/...`, resolved against
 * `BASE_API_URL` (REACT-28).
 * @returns the parsed JSON body, typed as `T`
 * @note On failure it logs at `error` level and throws: a `SafeFetchError` for a non-2xx
 * response, and an `Error` (with the original as `cause`) when the request fails, its
 * body cannot be read, or a successful response is not JSON.
 * @example
 * ```ts
 * const responseData = await safeFetch.call<HealthCheckResponse>(
 *   { name: fetchHealthCheck.name },
 *   { requestPathname: '/api/health-check', fetchOpts: { method: 'GET' } },
 * );
 * ```
 */
async function call<T>(
  { name }: { name: string },
  { fetchOpts, requestPathname }: { fetchOpts?: RequestInit; requestPathname: string },
): Promise<T> {
  const requestURL = `${BASE_API_URL}${requestPathname}`;

  const response = await (async function () {
    try {
      return await fetch(requestURL, fetchOpts);
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      logger.error(`[${name}] : request to '${requestURL}' did not complete`, err);
      throw new Error(`[${name}] : ERROR requesting '${requestURL}' - ${err.message}`, {
        cause: err,
      });
    }
  })();

  // NOTE: `fetch` resolves once headers arrive; reading the body can still fail.
  const responseText = await (async function () {
    try {
      return await response.text();
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      logger.error(`[${name}] : response body from '${requestURL}' was not read`, err);
      throw new Error(`[${name}] : ERROR reading '${requestURL}' - ${err.message}`, {
        cause: err,
      });
    }
  })();
  const parsedBody = safeParseJSON(responseText);

  if (!response.ok) {
    const fetchError = new SafeFetchError({
      callerName: name,
      detail: extractDetail(parsedBody),
      requestURL,
      status: response.status,
    });
    logger.error(`[${name}] : request to '${requestURL}' failed`, fetchError);
    throw fetchError;
  }

  if (parsedBody == null) {
    const parseError = new Error(
      `[${name}] : Expected a JSON body from '${requestURL}'. Received '${responseText.slice(0, 80)}'`,
    );
    logger.error(`[${name}] : response from '${requestURL}' was not JSON`, parseError);
    throw parseError;
  }

  // NOTE: the API contract types the body; `T` is the generated response type (MONO-15).
  return parsedBody as T;
}

export const safeFetch = { call };
