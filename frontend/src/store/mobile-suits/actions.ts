import type { MobileSuitCardEntity, MobileSuitsListResponse, PageMeta } from '@/api';
import {
  REQUEST_MOBILE_SUITS, // force formatting
  SET_MOBILE_SUITS,
  SET_MOBILE_SUITS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogList } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';

export function requestMobileSuits({
  dispatch,
  query,
}: BaseAction & { query: string }): void {
  return dispatch({ type: REQUEST_MOBILE_SUITS, payload: { mobileSuits: { query } } });
}

export function setMobileSuits({
  dispatch,
  items,
  meta,
  query,
}: BaseAction & {
  items: MobileSuitCardEntity[];
  meta: PageMeta;
  query: string;
}): void {
  return dispatch({
    type: SET_MOBILE_SUITS,
    payload: { mobileSuits: { items, meta, query } },
  });
}

export function setMobileSuitsError({
  dispatch,
  errorMessage,
  query,
}: BaseAction & { errorMessage: string; query: string }): void {
  return dispatch({
    type: SET_MOBILE_SUITS_ERROR,
    payload: { mobileSuits: { errorMessage, query } },
  });
}

/**
 * @description Requests one page of `GET /api/mobile-suits` for `query` (the API query string,
 * without `?`) and stores it.
 */
export async function fetchMobileSuits({
  dispatch,
  query,
}: BaseAction & { query: string }): Promise<void> {
  return fetchCatalogList<MobileSuitsListResponse>({
    listPath: '/api/mobile-suits',
    name: fetchMobileSuits.name,
    onError: (errorMessage) => setMobileSuitsError({ dispatch, errorMessage, query }),
    onRequest: () => requestMobileSuits({ dispatch, query }),
    onSuccess: ({ data, meta }) =>
      setMobileSuits({ dispatch, items: data, meta, query }),
    query,
  });
}
