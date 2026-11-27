import type {
  MobileSuitOrganizationRole,
  OrganizationCardEntity,
  OrganizationDetailEntity,
  OrganizationMobileSuitEntity,
  OrganizationMobileSuitsListResponse,
  OrganizationResponse,
  OrganizationsListResponse,
  PageMeta,
} from '@/api';
import {
  REQUEST_ORGANIZATION,
  REQUEST_ORGANIZATION_MOBILE_SUITS,
  REQUEST_ORGANIZATIONS,
  SET_ORGANIZATION,
  SET_ORGANIZATION_ERROR,
  SET_ORGANIZATION_MOBILE_SUITS,
  SET_ORGANIZATION_MOBILE_SUITS_ERROR,
  SET_ORGANIZATIONS,
  SET_ORGANIZATIONS_ERROR,
} from '@/store/actionTypes';
import {
  fetchCatalogDetail,
  fetchCatalogList,
  fetchCatalogSubList,
  type SubListRequest,
} from '@/store/catalogList';
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

type RoleSection = { role: MobileSuitOrganizationRole };

/**
 * @description Marks one role section's suits as loading for `query`, a `subListKey`.
 */
export function requestOrganizationMobileSuits({
  dispatch,
  query,
  role,
}: BaseAction & RoleSection & { query: string }): void {
  return dispatch({
    type: REQUEST_ORGANIZATION_MOBILE_SUITS,
    payload: { organizations: { query, role } },
  });
}

/** @description Stores one page of a role section's suits, unless a newer request has replaced it. */
export function setOrganizationMobileSuits({
  dispatch,
  items,
  meta,
  query,
  role,
}: BaseAction &
  RoleSection & {
    items: OrganizationMobileSuitEntity[];
    meta: PageMeta;
    query: string;
  }): void {
  return dispatch({
    type: SET_ORGANIZATION_MOBILE_SUITS,
    payload: { organizations: { items, meta, query, role } },
  });
}

/** @description Stores the error for a role section's suits, unless a newer request has replaced it. */
export function setOrganizationMobileSuitsError({
  dispatch,
  errorMessage,
  query,
  role,
}: BaseAction & RoleSection & { errorMessage: string; query: string }): void {
  return dispatch({
    type: SET_ORGANIZATION_MOBILE_SUITS_ERROR,
    payload: { organizations: { errorMessage, query, role } },
  });
}

/**
 * @description Requests one page of `GET /api/organizations/{organization_slug}/mobile-suits`
 * for `query` (the API query string, without `?`) and stores it in `role`'s section, under
 * `subListKey`.
 * @note `query` carries the section's `role=` itself (`roleSectionQuery`), so each
 * section's key differs. `slug` is the organization's current slug, from its detail.
 */
export async function fetchOrganizationMobileSuits({
  dispatch,
  query,
  role,
  slug,
}: BaseAction & RoleSection & SubListRequest): Promise<void> {
  return fetchCatalogSubList<OrganizationMobileSuitsListResponse>({
    name: fetchOrganizationMobileSuits.name,
    onError: (payload) =>
      setOrganizationMobileSuitsError({ dispatch, ...payload, role }),
    onRequest: (payload) =>
      requestOrganizationMobileSuits({ dispatch, ...payload, role }),
    onSuccess: (payload) => setOrganizationMobileSuits({ dispatch, ...payload, role }),
    parentPath: '/api/organizations',
    query,
    slug,
  });
}
