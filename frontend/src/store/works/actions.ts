import type {
  MobileSuitAppearanceCardEntity,
  PageMeta,
  WorkCardEntity,
  WorkDetailEntity,
  WorkMobileSuitsListResponse,
  WorkResponse,
  WorksListResponse,
} from '@/api';
import {
  REQUEST_WORK,
  REQUEST_WORK_MOBILE_SUITS,
  REQUEST_WORKS,
  SET_WORK,
  SET_WORK_ERROR,
  SET_WORK_MOBILE_SUITS,
  SET_WORK_MOBILE_SUITS_ERROR,
  SET_WORKS,
  SET_WORKS_ERROR,
} from '@/store/actionTypes';
import {
  fetchCatalogDetail,
  fetchCatalogList,
  subListKey,
  type SubListRequest,
} from '@/store/catalogList';
import type { BaseAction } from '@/store/types';

/** @description Marks the works list as loading for `query`. */
export function requestWorks({
  dispatch,
  query,
}: BaseAction & { query: string }): void {
  return dispatch({ type: REQUEST_WORKS, payload: { works: { query } } });
}

/** @description Stores one page of works for `query`, unless a newer request has replaced it. */
export function setWorks({
  dispatch,
  items,
  meta,
  query,
}: BaseAction & { items: WorkCardEntity[]; meta: PageMeta; query: string }): void {
  return dispatch({ type: SET_WORKS, payload: { works: { items, meta, query } } });
}

/** @description Stores the error for `query`, unless a newer request has replaced it. */
export function setWorksError({
  dispatch,
  errorMessage,
  query,
}: BaseAction & { errorMessage: string; query: string }): void {
  return dispatch({
    type: SET_WORKS_ERROR,
    payload: { works: { errorMessage, query } },
  });
}

/**
 * @description Requests one page of `GET /api/works` for `query` (the API query string,
 * without `?`) and stores it.
 */
export async function fetchWorks({
  dispatch,
  query,
}: BaseAction & { query: string }): Promise<void> {
  return fetchCatalogList<WorksListResponse>({
    listPath: '/api/works',
    name: fetchWorks.name,
    onError: (errorMessage) => setWorksError({ dispatch, errorMessage, query }),
    onRequest: () => requestWorks({ dispatch, query }),
    onSuccess: ({ data, meta }) => setWorks({ dispatch, items: data, meta, query }),
    query,
  });
}

/** @description Marks the work under `slug` as loading. */
export function requestWork({ dispatch, slug }: BaseAction & { slug: string }): void {
  return dispatch({ type: REQUEST_WORK, payload: { works: { slug } } });
}

/** @description Stores the work fetched for `slug`. */
export function setWork({
  detail,
  dispatch,
  slug,
}: BaseAction & { detail: WorkDetailEntity; slug: string }): void {
  return dispatch({ type: SET_WORK, payload: { works: { detail, slug } } });
}

/** @description Stores the error for the work under `slug`; `isNotFound` marks a 404. */
export function setWorkError({
  dispatch,
  errorMessage,
  isNotFound,
  slug,
}: BaseAction & { errorMessage: string; isNotFound: boolean; slug: string }): void {
  return dispatch({
    type: SET_WORK_ERROR,
    payload: { works: { errorMessage, isNotFound, slug } },
  });
}

/**
 * @description Requests `GET /api/works/{work_slug}` and stores the work under `slug`,
 * the slug asked for. An old slug stores the renamed work, whose `slug` is current.
 * @note A failed request does not throw: `safeFetch` has already logged it.
 */
export async function fetchWork({
  dispatch,
  slug,
}: BaseAction & { slug: string }): Promise<void> {
  return fetchCatalogDetail<WorkResponse>({
    detailPath: `/api/works/${encodeURIComponent(slug)}`,
    fallbackErrorMessage: 'The work request failed.',
    name: fetchWork.name,
    onError: ({ errorMessage, isNotFound }) =>
      setWorkError({ dispatch, errorMessage, isNotFound, slug }),
    onRequest: () => requestWork({ dispatch, slug }),
    onSuccess: (detail) => setWork({ detail, dispatch, slug }),
  });
}

/**
 * @description Marks the work's suits as loading for `query`, a `subListKey`.
 */
export function requestWorkMobileSuits({
  dispatch,
  query,
}: BaseAction & { query: string }): void {
  return dispatch({ type: REQUEST_WORK_MOBILE_SUITS, payload: { works: { query } } });
}

/** @description Stores one page of the work's suits, unless a newer request has replaced it. */
export function setWorkMobileSuits({
  dispatch,
  items,
  meta,
  query,
}: BaseAction & {
  items: MobileSuitAppearanceCardEntity[];
  meta: PageMeta;
  query: string;
}): void {
  return dispatch({
    type: SET_WORK_MOBILE_SUITS,
    payload: { works: { items, meta, query } },
  });
}

/** @description Stores the error for the work's suits, unless a newer request has replaced it. */
export function setWorkMobileSuitsError({
  dispatch,
  errorMessage,
  query,
}: BaseAction & { errorMessage: string; query: string }): void {
  return dispatch({
    type: SET_WORK_MOBILE_SUITS_ERROR,
    payload: { works: { errorMessage, query } },
  });
}

/**
 * @description Requests one page of `GET /api/works/{work_slug}/mobile-suits` for
 * `query` (the API query string, without `?`) and stores it under `subListKey`.
 * @note `slug` is the work's current slug, from its loaded detail.
 */
export async function fetchWorkMobileSuits({
  dispatch,
  query,
  slug,
}: BaseAction & SubListRequest): Promise<void> {
  const requestKey = subListKey({ query, slug });
  return fetchCatalogList<WorkMobileSuitsListResponse>({
    listPath: `/api/works/${encodeURIComponent(slug)}/mobile-suits`,
    name: fetchWorkMobileSuits.name,
    onError: (errorMessage) =>
      setWorkMobileSuitsError({ dispatch, errorMessage, query: requestKey }),
    onRequest: () => requestWorkMobileSuits({ dispatch, query: requestKey }),
    onSuccess: ({ data, meta }) =>
      setWorkMobileSuits({ dispatch, items: data, meta, query: requestKey }),
    query,
  });
}
