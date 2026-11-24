import type {
  PageMeta,
  WorkCardEntity,
  WorkDetailEntity,
  WorkResponse,
  WorksListResponse,
} from '@/api';
import {
  REQUEST_WORK,
  REQUEST_WORKS,
  SET_WORK,
  SET_WORK_ERROR,
  SET_WORKS,
  SET_WORKS_ERROR,
} from '@/store/actionTypes';
import { catalogErrorMessage, fetchCatalogList } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';
import { safeFetch, SafeFetchError } from '@/utils';

export function requestWorks({
  dispatch,
  query,
}: BaseAction & { query: string }): void {
  return dispatch({ type: REQUEST_WORKS, payload: { works: { query } } });
}

export function setWorks({
  dispatch,
  items,
  meta,
  query,
}: BaseAction & { items: WorkCardEntity[]; meta: PageMeta; query: string }): void {
  return dispatch({ type: SET_WORKS, payload: { works: { items, meta, query } } });
}

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

export function requestWork({ dispatch, slug }: BaseAction & { slug: string }): void {
  return dispatch({ type: REQUEST_WORK, payload: { works: { slug } } });
}

export function setWork({
  detail,
  dispatch,
  slug,
}: BaseAction & { detail: WorkDetailEntity; slug: string }): void {
  return dispatch({ type: SET_WORK, payload: { works: { detail, slug } } });
}

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
  requestWork({ dispatch, slug });
  let responseData: WorkResponse;
  try {
    responseData = await safeFetch.call<WorkResponse>(
      { name: fetchWork.name },
      {
        fetchOpts: { method: 'GET' },
        requestPathname: `/api/works/${encodeURIComponent(slug)}`,
      },
    );
  } catch (error) {
    return setWorkError({
      dispatch,
      errorMessage: catalogErrorMessage({
        error,
        fallback: 'The work request failed.',
      }),
      isNotFound: error instanceof SafeFetchError && error.status === 404,
      slug,
    });
  }
  // NOTE: dispatched outside the try, so a store bug surfaces instead of reading as a failed request.
  return setWork({ detail: responseData.data, dispatch, slug });
}
