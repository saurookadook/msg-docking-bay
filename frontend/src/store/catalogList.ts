// What every catalog slice shares: the state of one paged list and of the details
// fetched by slug, the transitions their field reducers make, and the fetch they run.
import type { PageMeta, ValidationError } from '@/api';
import type { Nullable } from '@/types';
import { safeFetch, SafeFetchError } from '@/utils';

/**
 * @description One catalog list page, and the API query it answers.
 * @note `search` is set by the request, so a response for an older query (typing fast)
 * is dropped instead of replacing the newer one's page.
 */
export type ListState<Card> = {
  errorMessage: Nullable<string>;
  items: Card[];
  meta: Nullable<PageMeta>;
  requestInProgress: boolean;
  /** @description The API query string, without `?`, of the last request. */
  search: Nullable<string>;
};

export type ListRequestPayload = { search: string };
export type ListSetPayload<Card> = { items: Card[]; meta: PageMeta; search: string };
export type ListErrorPayload = { errorMessage: string; search: string };

export function createInitialListState<Card>(): ListState<Card> {
  return {
    errorMessage: null,
    items: [],
    meta: null,
    requestInProgress: false,
    search: null,
  };
}

/**
 * @description Starts loading a page. The current rows stay until the new ones arrive,
 * so a live search doesn't blank the roster on every keystroke.
 */
export function requestList<Card>(
  stateSlice: ListState<Card>,
  { search }: ListRequestPayload,
): ListState<Card> {
  return { ...stateSlice, errorMessage: null, requestInProgress: true, search };
}

/** @description Stores a page, unless a newer request has replaced its query. */
export function setList<Card>(
  stateSlice: ListState<Card>,
  { items, meta, search }: ListSetPayload<Card>,
): ListState<Card> {
  if (search !== stateSlice.search) return stateSlice;
  return {
    errorMessage: null,
    items: [...items],
    meta,
    requestInProgress: false,
    search,
  };
}

/** @description Stores a failed page, unless a newer request has replaced its query. */
export function setListError<Card>(
  stateSlice: ListState<Card>,
  { errorMessage, search }: ListErrorPayload,
): ListState<Card> {
  if (search !== stateSlice.search) return stateSlice;
  return { errorMessage, items: [], meta: null, requestInProgress: false, search };
}

/** @description One entity's detail, fetched by the slug a page asked for. */
export type DetailState<Detail> = {
  detail: Nullable<Detail>;
  errorMessage: Nullable<string>;
  /** @description `true` when the API answered 404: no row has that slug. */
  isNotFound: boolean;
  requestInProgress: boolean;
};

export type DetailRequestPayload = { slug: string };
export type DetailSetPayload<Detail> = { detail: Detail; slug: string };
export type DetailErrorPayload = {
  errorMessage: string;
  isNotFound: boolean;
  slug: string;
};

/** @description Details by the slug they were requested with, old or current. */
export type DetailsBySlug<Detail> = Record<string, DetailState<Detail>>;

export function requestDetail<Detail>(
  stateSlice: DetailsBySlug<Detail>,
  { slug }: DetailRequestPayload,
): DetailsBySlug<Detail> {
  return {
    ...stateSlice,
    [slug]: {
      detail: stateSlice[slug]?.detail ?? null,
      errorMessage: null,
      isNotFound: false,
      requestInProgress: true,
    },
  };
}

export function setDetail<Detail>(
  stateSlice: DetailsBySlug<Detail>,
  { detail, slug }: DetailSetPayload<Detail>,
): DetailsBySlug<Detail> {
  return {
    ...stateSlice,
    [slug]: { detail, errorMessage: null, isNotFound: false, requestInProgress: false },
  };
}

export function setDetailError<Detail>(
  stateSlice: DetailsBySlug<Detail>,
  { errorMessage, isNotFound, slug }: DetailErrorPayload,
): DetailsBySlug<Detail> {
  return {
    ...stateSlice,
    [slug]: { detail: null, errorMessage, isNotFound, requestInProgress: false },
  };
}

function isValidationErrorList(detail: unknown): detail is ValidationError[] {
  return (
    Array.isArray(detail) &&
    detail.every(
      (item: unknown) =>
        typeof item === 'object' && item != null && 'msg' in item && 'loc' in item,
    )
  );
}

/**
 * @description The message to show for a failed catalog request: the API's `detail`
 * (FAPI-13), each 422 error as `<param>: <msg>`, or `fallback`.
 */
export function catalogErrorMessage({
  error,
  fallback,
}: {
  error: unknown;
  fallback: string;
}): string {
  if (!(error instanceof SafeFetchError)) return fallback;
  if (typeof error.detail === 'string') return error.detail;
  if (isValidationErrorList(error.detail) && error.detail.length > 0) {
    return error.detail
      .map(({ loc, msg }) => `${String(loc.at(-1) ?? 'request')}: ${msg}`)
      .join('; ');
  }
  return fallback;
}

/**
 * @description Requests one page of a catalog list: dispatches the request, then the
 * page or the error. Each slice's `fetch<Kind>` wraps it with its own actions.
 * @note A failed request does not throw: `safeFetch` has already logged it.
 */
export async function fetchCatalogList<Card>({
  listPath,
  name,
  onError,
  onRequest,
  onSuccess,
  search,
}: {
  listPath: string;
  name: string;
  onError: (errorMessage: string) => void;
  onRequest: () => void;
  onSuccess: (page: { data: Card[]; meta: PageMeta }) => void;
  search: string;
}): Promise<void> {
  onRequest();
  try {
    const responseData = await safeFetch.call<{ data: Card[]; meta: PageMeta }>(
      { name },
      {
        fetchOpts: { method: 'GET' },
        requestPathname: search === '' ? listPath : `${listPath}?${search}`,
      },
    );
    return onSuccess(responseData);
  } catch (error) {
    return onError(
      catalogErrorMessage({ error, fallback: 'The catalog request failed.' }),
    );
  }
}
