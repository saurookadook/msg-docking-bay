import type {
  OrganizationCardEntity,
  OrganizationsListResponse,
  PageMeta,
} from '@/api';
import {
  REQUEST_ORGANIZATIONS, // force formatting
  SET_ORGANIZATIONS,
  SET_ORGANIZATIONS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogList } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';

/** @description Marks the organizations list as loading for `query`. */
export function requestOrganizations({
  dispatch,
  query,
}: BaseAction & { query: string }): void {
  return dispatch({
    type: REQUEST_ORGANIZATIONS,
    payload: { organizations: { query } },
  });
}

/** @description Stores one page of organizations for `query`, unless a newer request has replaced it. */
export function setOrganizations({
  dispatch,
  items,
  meta,
  query,
}: BaseAction & {
  items: OrganizationCardEntity[];
  meta: PageMeta;
  query: string;
}): void {
  return dispatch({
    type: SET_ORGANIZATIONS,
    payload: { organizations: { items, meta, query } },
  });
}

/** @description Stores the error for `query`, unless a newer request has replaced it. */
export function setOrganizationsError({
  dispatch,
  errorMessage,
  query,
}: BaseAction & { errorMessage: string; query: string }): void {
  return dispatch({
    type: SET_ORGANIZATIONS_ERROR,
    payload: { organizations: { errorMessage, query } },
  });
}

/**
 * @description Requests one page of `GET /api/organizations` for `query` (the API query string,
 * without `?`) and stores it.
 */
export async function fetchOrganizations({
  dispatch,
  query,
}: BaseAction & { query: string }): Promise<void> {
  return fetchCatalogList<OrganizationsListResponse>({
    listPath: '/api/organizations',
    name: fetchOrganizations.name,
    onError: (errorMessage) => setOrganizationsError({ dispatch, errorMessage, query }),
    onRequest: () => requestOrganizations({ dispatch, query }),
    onSuccess: ({ data, meta }) =>
      setOrganizations({ dispatch, items: data, meta, query }),
    query,
  });
}
