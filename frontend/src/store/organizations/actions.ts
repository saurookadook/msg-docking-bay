import type { OrganizationCardEntity, PageMeta } from '@/api';
import {
  REQUEST_ORGANIZATIONS, // force formatting
  SET_ORGANIZATIONS,
  SET_ORGANIZATIONS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogList } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';

export function requestOrganizations({
  dispatch,
  search,
}: BaseAction & { search: string }): void {
  return dispatch({
    type: REQUEST_ORGANIZATIONS,
    payload: { organizations: { search } },
  });
}

export function setOrganizations({
  dispatch,
  items,
  meta,
  search,
}: BaseAction & {
  items: OrganizationCardEntity[];
  meta: PageMeta;
  search: string;
}): void {
  return dispatch({
    type: SET_ORGANIZATIONS,
    payload: { organizations: { items, meta, search } },
  });
}

export function setOrganizationsError({
  dispatch,
  errorMessage,
  search,
}: BaseAction & { errorMessage: string; search: string }): void {
  return dispatch({
    type: SET_ORGANIZATIONS_ERROR,
    payload: { organizations: { errorMessage, search } },
  });
}

/**
 * @description Requests one page of `GET /api/organizations` for `search` (the API query string,
 * without `?`) and stores it.
 */
export async function fetchOrganizations({
  dispatch,
  search,
}: BaseAction & { search: string }): Promise<void> {
  return fetchCatalogList<OrganizationCardEntity>({
    listPath: '/api/organizations',
    name: fetchOrganizations.name,
    onError: (errorMessage) =>
      setOrganizationsError({ dispatch, errorMessage, search }),
    onRequest: () => requestOrganizations({ dispatch, search }),
    onSuccess: ({ data, meta }) =>
      setOrganizations({ dispatch, items: data, meta, search }),
    search,
  });
}
