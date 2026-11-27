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
  /**
   * @description The API query string, without `?`, of the last request. For a
   * sub-list, `subListKey`'s `<parent slug>?<query>`, so another parent's page is
   * dropped too.
   */
  query: Nullable<string>;
  requestInProgress: boolean;
};

/**
 * @description One sub-list page request: the parent's current slug, and the API query
 * string, without `?`.
 */
export type SubListRequest = { query: string; slug: string };

/**
 * @description The `query` a sub-list (`/{slug}/mobile-suits`) stores its page under: the
 * parent's slug and the API query, so a page for another parent never replaces this one.
 */
export function subListKey({ query, slug }: SubListRequest): string {
  return `${slug}?${query}`;
}

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

/** @description The parent slug a `subListKey` belongs to: everything before its `?`. */
function subListParent(key: Nullable<string>): Nullable<string> {
  if (key == null) return null;
  const queryStart = key.indexOf('?');
  return queryStart === -1 ? key : key.slice(0, queryStart);
}

/**
 * @description Starts loading a sub-list page (`query` is a `subListKey`). Another page
 * of the same parent keeps the current rows until the new ones arrive, as `requestList`
 * does; another parent's rows are dropped at once, so they never show on its page.
 */
export function requestSubList<Card>(
  stateSlice: ListState<Card>,
  { query }: ListRequestPayload,
): ListState<Card> {
  if (subListParent(stateSlice.query) === subListParent(query)) {
    return requestList(stateSlice, { query });
  }
  return { ...createInitialListState<Card>(), requestInProgress: true, query };
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

/**
 * @description Stores the detail fetched for `slug`, and under its current slug too when
 * `slug` is an old one, so swapping the URL to the current slug does not fetch it again.
 */
export function setDetailUnderSlugs<Detail extends { slug: string }>(
  stateSlice: DetailsBySlug<Detail>,
  { detail, slug }: DetailSetPayload<Detail>,
): DetailsBySlug<Detail> {
  const storedState = setDetail(stateSlice, { detail, slug });
  return detail.slug === slug
    ? storedState
    : setDetail(storedState, { detail, slug: detail.slug });
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

/**
 * @description Requests one page of a parent's sub-list (`<parentPath>/{slug}/mobile-suits`)
 * for `query`, as `fetchCatalogList` does, with every payload keyed by `subListKey`.
 * Each slice's `fetch<Kind>MobileSuits` wraps it with its own actions.
 * @note `slug` is the parent's current slug, from its loaded detail.
 */
export async function fetchCatalogSubList<Response extends ListPage<unknown>>({
  name,
  onError,
  onRequest,
  onSuccess,
  parentPath,
  query,
  slug,
}: SubListRequest & {
  name: string;
  onError: (payload: ListErrorPayload) => void;
  onRequest: (payload: ListRequestPayload) => void;
  onSuccess: (payload: ListSetPayload<Response['data'][number]>) => void;
  /** @description The parent kind's API path, like `/api/works`. */
  parentPath: string;
}): Promise<void> {
  const key = subListKey({ query, slug });
  return fetchCatalogList<Response>({
    listPath: `${parentPath}/${encodeURIComponent(slug)}/mobile-suits`,
    name,
    onError: (errorMessage) => onError({ errorMessage, query: key }),
    onRequest: () => onRequest({ query: key }),
    onSuccess: ({ data, meta }) => onSuccess({ items: data, meta, query: key }),
    query,
  });
}

/**
 * @description Requests one entity's detail: dispatches the request, then the detail or
 * the error, with `isNotFound` set on a 404. Each slice's `fetch<Kind>` wraps it with its
 * own actions.
 * @note A failed request does not throw: `safeFetch` has already logged it.
 */
export async function fetchCatalogDetail<Response extends { data: unknown }>({
  detailPath,
  fallbackErrorMessage,
  name,
  onError,
  onRequest,
  onSuccess,
}: {
  /** @description The detail route's path, with the slug already encoded. */
  detailPath: string;
  fallbackErrorMessage: string;
  name: string;
  onError: (args: { errorMessage: string; isNotFound: boolean }) => void;
  onRequest: () => void;
  onSuccess: (detail: Response['data']) => void;
}): Promise<void> {
  onRequest();
  let responseData: Response;
  try {
    responseData = await safeFetch.call<Response>(
      { name },
      { fetchOpts: { method: 'GET' }, requestPathname: detailPath },
    );
  } catch (error) {
    return onError({
      errorMessage: catalogErrorMessage({ error, fallback: fallbackErrorMessage }),
      isNotFound: error instanceof SafeFetchError && error.status === 404,
    });
  }
  // NOTE: called outside the try, so a store bug surfaces instead of reading as a failed request.
  return onSuccess(responseData.data);
}
