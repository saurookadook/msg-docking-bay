import type {
  MechanicalDesignerCardEntity,
  MechanicalDesignerDetailEntity,
  MechanicalDesignerResponse,
  MechanicalDesignersListResponse,
  PageMeta,
} from '@/api';
import {
  REQUEST_MECHANICAL_DESIGNER,
  REQUEST_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNER,
  SET_MECHANICAL_DESIGNER_ERROR,
  SET_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNERS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogDetail, fetchCatalogList } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';

/** @description Marks the designers list as loading for `query`. */
export function requestMechanicalDesigners({
  dispatch,
  query,
}: BaseAction & { query: string }): void {
  return dispatch({
    type: REQUEST_MECHANICAL_DESIGNERS,
    payload: { mechanicalDesigners: { query } },
  });
}

/** @description Stores one page of designers for `query`, unless a newer request has replaced it. */
export function setMechanicalDesigners({
  dispatch,
  items,
  meta,
  query,
}: BaseAction & {
  items: MechanicalDesignerCardEntity[];
  meta: PageMeta;
  query: string;
}): void {
  return dispatch({
    type: SET_MECHANICAL_DESIGNERS,
    payload: { mechanicalDesigners: { items, meta, query } },
  });
}

/** @description Stores the error for `query`, unless a newer request has replaced it. */
export function setMechanicalDesignersError({
  dispatch,
  errorMessage,
  query,
}: BaseAction & { errorMessage: string; query: string }): void {
  return dispatch({
    type: SET_MECHANICAL_DESIGNERS_ERROR,
    payload: { mechanicalDesigners: { errorMessage, query } },
  });
}

/**
 * @description Requests one page of `GET /api/mechanical-designers` for `query` (the API query string,
 * without `?`) and stores it.
 */
export async function fetchMechanicalDesigners({
  dispatch,
  query,
}: BaseAction & { query: string }): Promise<void> {
  return fetchCatalogList<MechanicalDesignersListResponse>({
    listPath: '/api/mechanical-designers',
    name: fetchMechanicalDesigners.name,
    onError: (errorMessage) =>
      setMechanicalDesignersError({ dispatch, errorMessage, query }),
    onRequest: () => requestMechanicalDesigners({ dispatch, query }),
    onSuccess: ({ data, meta }) =>
      setMechanicalDesigners({ dispatch, items: data, meta, query }),
    query,
  });
}

/**
 * @description Marks the mechanical designer under `slug` as loading.
 * @note `slug` is the URL slug asked for (`hajime-katoki`): an old one too.
 */
export function requestMechanicalDesigner({
  dispatch,
  slug,
}: BaseAction & { slug: string }): void {
  return dispatch({
    type: REQUEST_MECHANICAL_DESIGNER,
    payload: { mechanicalDesigners: { slug } },
  });
}

/**
 * @description Stores the mechanical designer fetched for `slug`.
 * @note `slug` is the URL slug asked for (`hajime-katoki`): an old one too.
 */
export function setMechanicalDesigner({
  detail,
  dispatch,
  slug,
}: BaseAction & { detail: MechanicalDesignerDetailEntity; slug: string }): void {
  return dispatch({
    type: SET_MECHANICAL_DESIGNER,
    payload: { mechanicalDesigners: { detail, slug } },
  });
}

/**
 * @description Stores the error for the mechanical designer under `slug`; `isNotFound` marks a 404.
 * @note `slug` is the URL slug asked for (`hajime-katoki`): an old one too.
 */
export function setMechanicalDesignerError({
  dispatch,
  errorMessage,
  isNotFound,
  slug,
}: BaseAction & { errorMessage: string; isNotFound: boolean; slug: string }): void {
  return dispatch({
    type: SET_MECHANICAL_DESIGNER_ERROR,
    payload: { mechanicalDesigners: { errorMessage, isNotFound, slug } },
  });
}

/**
 * @description Requests `GET /api/mechanical-designers/{mechanical_designer_slug}` and stores the mechanical designer under
 * `slug`, the slug asked for. An old slug stores the renamed mechanical designer, whose `slug` is
 * current, under both.
 */
export async function fetchMechanicalDesigner({
  dispatch,
  slug,
}: BaseAction & { slug: string }): Promise<void> {
  return fetchCatalogDetail<MechanicalDesignerResponse>({
    detailPath: `/api/mechanical-designers/${encodeURIComponent(slug)}`,
    fallbackErrorMessage: 'The mechanical designer request failed.',
    name: fetchMechanicalDesigner.name,
    onError: ({ errorMessage, isNotFound }) =>
      setMechanicalDesignerError({ dispatch, errorMessage, isNotFound, slug }),
    onRequest: () => requestMechanicalDesigner({ dispatch, slug }),
    onSuccess: (detail) => setMechanicalDesigner({ detail, dispatch, slug }),
  });
}
