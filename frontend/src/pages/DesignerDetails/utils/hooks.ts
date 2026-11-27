import type { DesignedMobileSuitEntity } from '@/api';
import {
  fetchMechanicalDesignerMobileSuits,
  useCatalogSubList,
  type AppState,
  type ListState,
} from '@/store';
import { listSearch } from '@/utils';

const SUB_LIST_KEYS = ['limit', 'offset'] as const;

const apiQuery = (searchParams: URLSearchParams) =>
  listSearch({ keys: SUB_LIST_KEYS, searchParams });

const selectDesignedUnits = (appState: AppState) =>
  appState.mechanicalDesigners.mobileSuits;

/**
 * @description The page of the designer's credits the URL asks for, loaded once the
 * designer is.
 * @note `slug` is the designer's current slug, from their loaded detail.
 */
export function useDesignedUnits(slug: string): ListState<DesignedMobileSuitEntity> {
  return useCatalogSubList({
    apiQuery,
    fetchSubList: fetchMechanicalDesignerMobileSuits,
    selectList: selectDesignedUnits,
    slug,
  });
}
