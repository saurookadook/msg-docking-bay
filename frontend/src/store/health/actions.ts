import {
  REQUEST_HEALTH_CHECK, // force formatting
  SET_HEALTH_CHECK,
  SET_HEALTH_CHECK_ERROR,
} from '@/store/actionTypes';
import type { BaseAction } from '@/store/types';
import type { HealthCheck, HealthCheckResponse } from '@/types';
import { safeFetch, SafeFetchError } from '@/utils';

const FALLBACK_HEALTH_CHECK_ERROR_MESSAGE = 'The health check request failed.';

export function requestHealthCheck({ dispatch }: BaseAction) {
  return dispatch({ type: REQUEST_HEALTH_CHECK });
}

export function setHealthCheck({
  dispatch, // force formatting
  healthCheck,
}: BaseAction & { healthCheck: HealthCheck }) {
  return dispatch({ type: SET_HEALTH_CHECK, payload: { health: { healthCheck } } });
}

export function setHealthCheckError({
  dispatch, // force formatting
  errorMessage,
}: BaseAction & { errorMessage: string }) {
  return dispatch({
    type: SET_HEALTH_CHECK_ERROR,
    payload: { health: { errorMessage } },
  });
}

/**
 * @description Requests `GET /api/health-check` and stores the result.
 * @note A failed request does not throw: `safeFetch` has already logged it, and this
 * stores the API's `detail` (or a fallback message) for the page to show.
 */
export async function fetchHealthCheck({ dispatch }: BaseAction): Promise<void> {
  requestHealthCheck({ dispatch });

  try {
    const responseData = await safeFetch.call<HealthCheckResponse>(
      { name: fetchHealthCheck.name },
      { requestPathname: '/api/health-check', fetchOpts: { method: 'GET' } },
    );
    return setHealthCheck({ dispatch, healthCheck: responseData.data });
  } catch (error) {
    const errorMessage =
      error instanceof SafeFetchError && typeof error.detail === 'string'
        ? error.detail
        : FALLBACK_HEALTH_CHECK_ERROR_MESSAGE;
    return setHealthCheckError({ dispatch, errorMessage });
  }
}
