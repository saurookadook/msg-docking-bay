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

export function requestMechanicalDesigners({
  dispatch,
  search,
}: BaseAction & { search: string }): void {
  return dispatch({
    type: REQUEST_MECHANICAL_DESIGNERS,
    payload: { mechanicalDesigners: { search } },
  });
}

export function setMechanicalDesigners({
  dispatch,
  items,
  meta,
  search,
}: BaseAction & {
  items: MechanicalDesignerCardEntity[];
  meta: PageMeta;
  search: string;
}): void {
  return dispatch({
    type: SET_MECHANICAL_DESIGNERS,
    payload: { mechanicalDesigners: { items, meta, search } },
  });
}

export function setMechanicalDesignersError({
  dispatch,
  errorMessage,
  search,
}: BaseAction & { errorMessage: string; search: string }): void {
  return dispatch({
    type: SET_MECHANICAL_DESIGNERS_ERROR,
    payload: { mechanicalDesigners: { errorMessage, search } },
  });
}

/**
 * @description Requests one page of `GET /api/mechanical-designers` for `search` (the API query string,
 * without `?`) and stores it.
 */
export async function fetchMechanicalDesigners({
  dispatch,
  search,
}: BaseAction & { search: string }): Promise<void> {
  return fetchCatalogList<MechanicalDesignersListResponse>({
    listPath: '/api/mechanical-designers',
    name: fetchMechanicalDesigners.name,
    onError: (errorMessage) =>
      setMechanicalDesignersError({ dispatch, errorMessage, search }),
    onRequest: () => requestMechanicalDesigners({ dispatch, search }),
    onSuccess: ({ data, meta }) =>
      setMechanicalDesigners({ dispatch, items: data, meta, search }),
    search,
  });
}
