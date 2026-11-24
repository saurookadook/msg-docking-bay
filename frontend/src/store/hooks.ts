import { use, useEffect } from 'react';
import { useSearchParams } from 'react-router';

import { listSearch, withSearchParam } from '@/utils';

import type { ListState } from './catalogList';
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
  fetchList: (args: BaseAction & { search: string }) => Promise<void>;
  keys: readonly string[];
  selectList: (appState: AppState) => ListState<Card>;
}): ListState<Card> {
  const { appDispatch, appState } = useAppStore();
  const [searchParams] = useSearchParams();
  const search = listSearch({ keys, searchParams });

  useEffect(() => {
    let isActive = true;
    void fetchList({
      dispatch: guardDispatch({ dispatch: appDispatch, isActive: () => isActive }),
      search,
    });
    return () => {
      isActive = false;
    };
  }, [appDispatch, fetchList, search]);

  return selectList(appState);
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

/**
 * @description The filter bar chip for the URL's `work`, titled from the works slice.
 * An old slug is swapped in the URL for the work's current one, since the list
 * filters match current slugs only.
 * @returns no chip while `work` is unset
 */
export function useWorkFilterChips(): {
  label: string;
  param: string;
  valueLabel: string;
}[] {
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
    setSearchParams(
      (previous) =>
        withSearchParam({ name: 'work', searchParams: previous, value: currentSlug }),
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
