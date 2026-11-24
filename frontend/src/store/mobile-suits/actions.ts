import type { MobileSuitCardEntity, PageMeta } from '@/api';
import {
  REQUEST_MOBILE_SUITS, // force formatting
  SET_MOBILE_SUITS,
  SET_MOBILE_SUITS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogList } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';

export function requestMobileSuits({
  dispatch,
  search,
}: BaseAction & { search: string }): void {
  return dispatch({ type: REQUEST_MOBILE_SUITS, payload: { mobileSuits: { search } } });
}

export function setMobileSuits({
  dispatch,
  items,
  meta,
  search,
}: BaseAction & {
  items: MobileSuitCardEntity[];
  meta: PageMeta;
  search: string;
}): void {
  return dispatch({
    type: SET_MOBILE_SUITS,
    payload: { mobileSuits: { items, meta, search } },
  });
}

export function setMobileSuitsError({
  dispatch,
  errorMessage,
  search,
}: BaseAction & { errorMessage: string; search: string }): void {
  return dispatch({
    type: SET_MOBILE_SUITS_ERROR,
    payload: { mobileSuits: { errorMessage, search } },
  });
}

/**
 * @description Requests one page of `GET /api/mobile-suits` for `search` (the API query string,
 * without `?`) and stores it.
 */
export async function fetchMobileSuits({
  dispatch,
  search,
}: BaseAction & { search: string }): Promise<void> {
  return fetchCatalogList<MobileSuitCardEntity>({
    listPath: '/api/mobile-suits',
    name: fetchMobileSuits.name,
    onError: (errorMessage) => setMobileSuitsError({ dispatch, errorMessage, search }),
    onRequest: () => requestMobileSuits({ dispatch, search }),
    onSuccess: ({ data, meta }) =>
      setMobileSuits({ dispatch, items: data, meta, search }),
    search,
  });
}
