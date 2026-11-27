import { use, useEffect } from 'react';
import { useSearchParams } from 'react-router';

import type { FilterBarChip } from '@/components';
import type { Nullable } from '@/types';
import { listSearch } from '@/utils';

import {
  createInitialListState,
  subListKey,
  type DetailsBySlug,
  type DetailState,
  type ListState,
  type SubListRequest,
} from './catalogList';
import { AppStoreContext, type AppStoreContextValue } from './context';
import { fetchContinuities } from './continuities/actions';
import type { ContinuitiesStateSlice } from './continuities/reducer.types';
import type { AppState } from './reducer';
import type { AppDispatch, BaseAction } from './types';
import { fetchWork } from './works/actions';

/** @description Reads and writes the app store (REACT-18). */
export function useAppStore(): AppStoreContextValue {
  const storeValue = use(AppStoreContext);
  if (storeValue == null) {
    throw new Error('[useAppStore] : must be called inside <AppStoreProvider>');
  }
  return storeValue;
}

/**
 * @description A dispatch that does nothing once `isActive()` is false, so a request
 * still pending after its page moved on can't overwrite newer state.
 */
function guardDispatch({
  dispatch,
  isActive,
}: {
  dispatch: AppDispatch;
  isActive: () => boolean;
}): AppDispatch {
  return (action) => {
    if (isActive()) dispatch(action);
  };
}

/**
 * @description Loads the catalog page the URL asks for, and returns it. The API query
 * is built from `keys` only, so other params never reach the API.
 * @note It refetches whenever that query changes; the slice drops a response for an
 * older query, and the effect's guard drops one that lands after the page unmounts.
 */
export function useCatalogList<Card>({
  fetchList,
  keys,
  selectList,
}: {
  fetchList: (args: BaseAction & { query: string }) => Promise<void>;
  keys: readonly string[];
  selectList: (appState: AppState) => ListState<Card>;
}): ListState<Card> {
  const { appDispatch, appState } = useAppStore();
  const [searchParams] = useSearchParams();
  const query = listSearch({ keys, searchParams });

  useEffect(() => {
    let isActive = true;
    void fetchList({
      dispatch: guardDispatch({ dispatch: appDispatch, isActive: () => isActive }),
      query,
    });
    return () => {
      isActive = false;
    };
  }, [appDispatch, fetchList, query]);

  return selectList(appState);
}

/**
 * @description Loads the detail for `slug` once, and returns its state.
 * @returns `undefined` until the first request is dispatched
 * @note Details stay in the store, so returning to a page shows it without refetching.
 * No guard drops a late response: each slug's state is kept apart, so one that lands
 * after the page moved on is stored under its own slug and replaces nothing.
 * `slug` is the entity's URL slug from the route, which may be an old one.
 */
export function useCatalogDetail<Detail>({
  fetchDetail,
  selectDetails,
  slug,
}: {
  fetchDetail: (args: BaseAction & { slug: string }) => Promise<void>;
  selectDetails: (appState: AppState) => DetailsBySlug<Detail>;
  slug: string;
}): DetailState<Detail> | undefined {
  const { appDispatch, appState } = useAppStore();
  const detailState = selectDetails(appState)[slug];
  const shouldFetch = detailState === undefined;

  useEffect(() => {
    if (shouldFetch) void fetchDetail({ dispatch: appDispatch, slug });
  }, [appDispatch, fetchDetail, shouldFetch, slug]);

  return detailState;
}

/**
 * @description Loads the page of a parent's sub-list (`/{slug}/mobile-suits`) that the
 * URL asks for, and returns it. It waits for `slug`: the parent's current slug, from its
 * loaded detail, so an old-slug visit fetches once and a 404 comes from the detail.
 * @returns a loading list while the stored page belongs to another parent or query, so
 * the page never shows another parent's rows
 * @note `fetchSubList` and `apiQuery` must be stable (module-level), or every render
 * refetches. The effect's guard drops a response that lands after the page unmounts.
 */
export function useCatalogSubList<Item>({
  apiQuery,
  fetchSubList,
  selectList,
  slug,
}: {
  /** @description The API query string, without `?`, for the URL's search params. */
  apiQuery: (searchParams: URLSearchParams) => string;
  fetchSubList: (args: BaseAction & SubListRequest) => Promise<void>;
  selectList: (appState: AppState) => ListState<Item>;
  slug: Nullable<string>;
}): ListState<Item> {
  const { appDispatch, appState } = useAppStore();
  const [searchParams] = useSearchParams();
  const query = apiQuery(searchParams);
  const list = selectList(appState);

  useEffect(() => {
    if (slug == null) return;
    let isActive = true;
    void fetchSubList({
      dispatch: guardDispatch({ dispatch: appDispatch, isActive: () => isActive }),
      query,
      slug,
    });
    return () => {
      isActive = false;
    };
  }, [appDispatch, fetchSubList, query, slug]);

  if (slug != null && list.query === subListKey({ query, slug })) return list;
  return { ...createInitialListState<Item>(), requestInProgress: true };
}

/** @description Every continuity, loaded once for the whole app. */
export function useContinuities(): ContinuitiesStateSlice {
  const { appDispatch, appState } = useAppStore();
  const { continuities } = appState;
  const shouldFetch =
    !continuities.continuitiesLoaded &&
    !continuities.continuitiesRequestInProgress &&
    continuities.continuitiesErrorMessage == null;

  useEffect(() => {
    if (shouldFetch) void fetchContinuities({ dispatch: appDispatch });
  }, [appDispatch, shouldFetch]);

  return continuities;
}

/** @description Every continuity as a filter select option, loaded once. */
export function useContinuityOptions(): { label: string; value: string }[] {
  const { continuities } = useContinuities();
  return continuities.map(({ name, slug }) => ({ label: name, value: slug }));
}

/**
 * @description The filter bar chip for the URL's `work`, titled from the works slice.
 * An old slug is swapped in the URL for the work's current one, since the list
 * filters match current slugs only.
 * @returns no chip while `work` is unset
 */
export function useWorkFilterChips(): FilterBarChip[] {
  const { appDispatch, appState } = useAppStore();
  const [searchParams, setSearchParams] = useSearchParams();
  const workSlug = searchParams.get('work')?.trim() ?? '';
  const workState =
    workSlug === '' ? undefined : appState.works.detailsBySlug[workSlug];
  const currentSlug = workState?.detail?.slug;

  useEffect(() => {
    if (workSlug === '' || workState !== undefined) return;
    void fetchWork({ dispatch: appDispatch, slug: workSlug });
  }, [appDispatch, workSlug, workState]);

  useEffect(() => {
    if (currentSlug == null || currentSlug === workSlug) return;
    // NOTE: a plain set, not withSearchParam: the page itself has not changed, so keep offset.
    setSearchParams(
      (previous) => {
        const nextSearchParams = new URLSearchParams(previous);
        nextSearchParams.set('work', currentSlug);
        return nextSearchParams;
      },
      { replace: true },
    );
  }, [currentSlug, setSearchParams, workSlug]);

  if (workSlug === '') return [];
  const valueLabel = (function () {
    if (workState?.detail != null) return workState.detail.title;
    if (workState?.isNotFound === true) return `Unknown work (${workSlug})`;
    return workSlug;
  })();
  return [{ label: 'Work', param: 'work', valueLabel }];
}
