import type { MobileSuitAppearanceCardEntity } from '@/api';
import {
  fetchWorkMobileSuits,
  useCatalogSubList,
  type AppState,
  type ListState,
} from '@/store';

const selectWorkMobileSuits = (appState: AppState) => appState.works.mobileSuits;

/**
 * @description The page of the work's suits the URL asks for, loaded once the work is.
 * @note `slug` is the work's current slug, from its loaded detail.
 */
export function useWorkSuits(slug: string): ListState<MobileSuitAppearanceCardEntity> {
  return useCatalogSubList({
    fetchSubList: fetchWorkMobileSuits,
    selectList: selectWorkMobileSuits,
    slug,
  });
}
