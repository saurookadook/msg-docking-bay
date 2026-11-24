// NOTE: what every catalog slice shares: the state of one paged list and of the details
// fetched by slug, the transitions their field reducers make, and the fetch they run.
import type { PageMeta, ValidationError } from '@/api';
import type { Nullable } from '@/types';
import { safeFetch, SafeFetchError } from '@/utils';

/**
 * @description One catalog list page, and the API query it answers.
 * @note `query` is set by the request, so a response for an older query (typing fast)
 * is dropped instead of replacing the newer one's page.
 */
export type ListState<Card> = {
  errorMessage: Nullable<string>;
  items: Card[];
  meta: Nullable<PageMeta>;
  /** @description The API query string, without `?`, of the last request. */
  query: Nullable<string>;
  requestInProgress: boolean;
};

/** @description A catalog list route's 200 body: one page of cards and its paging. */
export type ListPage<Card> = { data: Card[]; meta: PageMeta };

export type ListRequestPayload = { query: string };
export type ListSetPayload<Card> = { items: Card[]; meta: PageMeta; query: string };
export type ListErrorPayload = { errorMessage: string; query: string };

/** @description A catalog list before its first request: empty, with no query. */
export function createInitialListState<Card>(): ListState<Card> {
  return {
    errorMessage: null,
    items: [],
    meta: null,
    requestInProgress: false,
    query: null,
  };
}

/**
 * @description Starts loading a page. The current rows stay until the new ones arrive,
 * so a live search doesn't blank the roster on every keystroke.
 */
export function requestList<Card>(
  stateSlice: ListState<Card>,
  { query }: ListRequestPayload,
): ListState<Card> {
  return { ...stateSlice, errorMessage: null, requestInProgress: true, query };
}

/** @description Stores a page, unless a newer request has replaced its query. */
export function setList<Card>(
  stateSlice: ListState<Card>,
  { items, meta, query }: ListSetPayload<Card>,
): ListState<Card> {
  if (query !== stateSlice.query) return stateSlice;
  return {
    errorMessage: null,
    items: [...items],
    meta,
    requestInProgress: false,
    query,
  };
}

/** @description Stores a failed page, unless a newer request has replaced its query. */
export function setListError<Card>(
  stateSlice: ListState<Card>,
  { errorMessage, query }: ListErrorPayload,
): ListState<Card> {
  if (query !== stateSlice.query) return stateSlice;
  return { errorMessage, items: [], meta: null, requestInProgress: false, query };
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

/** @description Marks the detail under `slug` as loading, keeping any detail already shown. */
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

/** @description Stores the detail fetched for `slug`. */
export function setDetail<Detail>(
  stateSlice: DetailsBySlug<Detail>,
  { detail, slug }: DetailSetPayload<Detail>,
): DetailsBySlug<Detail> {
  return {
    ...stateSlice,
    [slug]: { detail, errorMessage: null, isNotFound: false, requestInProgress: false },
  };
}

/** @description Stores the error for `slug`'s detail, with `detail` set to `null`. */
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
export async function fetchCatalogList<Response extends ListPage<unknown>>({
  listPath,
  name,
  onError,
  onRequest,
  onSuccess,
  query,
}: {
  listPath: string;
  name: string;
  onError: (errorMessage: string) => void;
  onRequest: () => void;
  onSuccess: (page: Response) => void;
  query: string;
}): Promise<void> {
  onRequest();
  let responseData: Response;
  try {
    responseData = await safeFetch.call<Response>(
      { name },
      {
        fetchOpts: { method: 'GET' },
        requestPathname: query === '' ? listPath : `${listPath}?${query}`,
      },
    );
  } catch (error) {
    return onError(
      catalogErrorMessage({ error, fallback: 'The catalog request failed.' }),
    );
  }
  // NOTE: called outside the try, so a store bug surfaces instead of reading as a failed request.
  return onSuccess(responseData);
}
