import type { ContinuitiesListResponse, ContinuityCardEntity } from '@/api';
import {
  REQUEST_CONTINUITIES, // force formatting
  SET_CONTINUITIES,
  SET_CONTINUITIES_ERROR,
} from '@/store/actionTypes';
import { catalogErrorMessage } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';
import { safeFetch } from '@/utils';

export function requestContinuities({ dispatch }: BaseAction): void {
  return dispatch({ type: REQUEST_CONTINUITIES });
}

export function setContinuities({
  continuities,
  dispatch,
}: BaseAction & { continuities: ContinuityCardEntity[] }): void {
  return dispatch({
    type: SET_CONTINUITIES,
    payload: { continuities: { continuities } },
  });
}

export function setContinuitiesError({
  dispatch,
  errorMessage,
}: BaseAction & { errorMessage: string }): void {
  return dispatch({
    type: SET_CONTINUITIES_ERROR,
    payload: { continuities: { errorMessage } },
  });
}

/**
 * @description Requests `GET /api/continuities` (every continuity, unpaged) and stores
 * them for the filters.
 * @note A failed request does not throw: `safeFetch` has already logged it.
 */
export async function fetchContinuities({ dispatch }: BaseAction): Promise<void> {
  requestContinuities({ dispatch });
  try {
    const responseData = await safeFetch.call<ContinuitiesListResponse>(
      { name: fetchContinuities.name },
      { fetchOpts: { method: 'GET' }, requestPathname: '/api/continuities' },
    );
    return setContinuities({ continuities: responseData.data, dispatch });
  } catch (error) {
    return setContinuitiesError({
      dispatch,
      errorMessage: catalogErrorMessage({
        error,
        fallback: 'The continuities request failed.',
      }),
    });
  }
}
