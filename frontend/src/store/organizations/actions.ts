import type {
  OrganizationCardEntity,
  OrganizationDetailEntity,
  OrganizationResponse,
  OrganizationsListResponse,
  PageMeta,
} from '@/api';
import {
  REQUEST_ORGANIZATION,
  REQUEST_ORGANIZATIONS,
  SET_ORGANIZATION,
  SET_ORGANIZATION_ERROR,
  SET_ORGANIZATIONS,
  SET_ORGANIZATIONS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogDetail, fetchCatalogList } from '@/store/catalogList';
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

/**
 * @description Marks the organization under `slug` as loading.
 * @note `slug` is the URL slug asked for (`earth-federation`): an old one too.
 */
export function requestOrganization({
  dispatch,
  slug,
}: BaseAction & { slug: string }): void {
  return dispatch({ type: REQUEST_ORGANIZATION, payload: { organizations: { slug } } });
}

/**
 * @description Stores the organization fetched for `slug`.
 * @note `slug` is the URL slug asked for (`earth-federation`): an old one too.
 */
export function setOrganization({
  detail,
  dispatch,
  slug,
}: BaseAction & { detail: OrganizationDetailEntity; slug: string }): void {
  return dispatch({
    type: SET_ORGANIZATION,
    payload: { organizations: { detail, slug } },
  });
}

/**
 * @description Stores the error for the organization under `slug`; `isNotFound` marks a 404.
 * @note `slug` is the URL slug asked for (`earth-federation`): an old one too.
 */
export function setOrganizationError({
  dispatch,
  errorMessage,
  isNotFound,
  slug,
}: BaseAction & { errorMessage: string; isNotFound: boolean; slug: string }): void {
  return dispatch({
    type: SET_ORGANIZATION_ERROR,
    payload: { organizations: { errorMessage, isNotFound, slug } },
  });
}

/**
 * @description Requests `GET /api/organizations/{organization_slug}` and stores the organization under
 * `slug`, the slug asked for. An old slug stores the renamed organization, whose `slug` is
 * current, under both.
 */
export async function fetchOrganization({
  dispatch,
  slug,
}: BaseAction & { slug: string }): Promise<void> {
  return fetchCatalogDetail<OrganizationResponse>({
    detailPath: `/api/organizations/${encodeURIComponent(slug)}`,
    fallbackErrorMessage: 'The organization request failed.',
    name: fetchOrganization.name,
    onError: ({ errorMessage, isNotFound }) =>
      setOrganizationError({ dispatch, errorMessage, isNotFound, slug }),
    onRequest: () => requestOrganization({ dispatch, slug }),
    onSuccess: (detail) => setOrganization({ detail, dispatch, slug }),
  });
}
