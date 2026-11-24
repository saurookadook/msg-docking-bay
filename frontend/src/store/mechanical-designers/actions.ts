import type {
  MechanicalDesignerCardEntity,
  MechanicalDesignersListResponse,
  PageMeta,
} from '@/api';
import {
  REQUEST_MECHANICAL_DESIGNERS, // force formatting
  SET_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNERS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogList } from '@/store/catalogList';
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
