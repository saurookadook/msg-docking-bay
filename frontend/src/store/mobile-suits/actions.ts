import type {
  MobileSuitCardEntity,
  MobileSuitDetailEntity,
  MobileSuitsListResponse,
  PageMeta,
} from '@/api';
import {
  REQUEST_MOBILE_SUIT,
  REQUEST_MOBILE_SUITS,
  SET_MOBILE_SUIT,
  SET_MOBILE_SUIT_ERROR,
  SET_MOBILE_SUITS,
  SET_MOBILE_SUITS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogDetail, fetchCatalogList } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';

/** @description Marks the mobile suits list as loading for `query`. */
export function requestMobileSuits({
  dispatch,
  query,
}: BaseAction & { query: string }): void {
  return dispatch({ type: REQUEST_MOBILE_SUITS, payload: { mobileSuits: { query } } });
}

/** @description Stores one page of mobile suits for `query`, unless a newer request has replaced it. */
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

/** @description Stores the error for `query`, unless a newer request has replaced it. */
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

/** @description Marks the mobile suit under `slug` as loading. */
export function requestMobileSuit({
  dispatch,
  slug,
}: BaseAction & { slug: string }): void {
  return dispatch({ type: REQUEST_MOBILE_SUIT, payload: { mobileSuits: { slug } } });
}

/** @description Stores the mobile suit fetched for `slug`. */
export function setMobileSuit({
  detail,
  dispatch,
  slug,
}: BaseAction & { detail: MobileSuitDetailEntity; slug: string }): void {
  return dispatch({
    type: SET_MOBILE_SUIT,
    payload: { mobileSuits: { detail, slug } },
  });
}

/** @description Stores the error for the mobile suit under `slug`; `isNotFound` marks a 404. */
export function setMobileSuitError({
  dispatch,
  errorMessage,
  isNotFound,
  slug,
}: BaseAction & { errorMessage: string; isNotFound: boolean; slug: string }): void {
  return dispatch({
    type: SET_MOBILE_SUIT_ERROR,
    payload: { mobileSuits: { errorMessage, isNotFound, slug } },
  });
}

/**
 * @description Requests `GET /api/mobile-suits/{mobile_suit_slug}` and stores the suit
 * under `slug`, the slug asked for. An old slug stores the renamed suit, whose `slug` is
 * current, under both.
 */
export async function fetchMobileSuit({
  dispatch,
  slug,
}: BaseAction & { slug: string }): Promise<void> {
  return fetchCatalogDetail<MobileSuitDetailEntity>({
    detailPath: `/api/mobile-suits/${encodeURIComponent(slug)}`,
    fallbackErrorMessage: 'The mobile suit request failed.',
    name: fetchMobileSuit.name,
    onError: ({ errorMessage, isNotFound }) =>
      setMobileSuitError({ dispatch, errorMessage, isNotFound, slug }),
    onRequest: () => requestMobileSuit({ dispatch, slug }),
    onSuccess: (detail) => setMobileSuit({ detail, dispatch, slug }),
  });
}
