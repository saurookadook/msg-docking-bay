import { useSearchParams } from 'react-router';

import type { MobileSuitSpecSheetEntity } from '@/api';
import type { Nullable } from '@/types';

import {
  selectSpecSheetIndex,
  SPEC_PARAM,
  specSheetEntries,
  type SpecSheetEntry,
} from './specSheets';

export type SpecSheetSelection = {
  entries: SpecSheetEntry[];
  /** @description The selected entry's place in `entries`. */
  index: number;
  /** @description The selected entry, or `null` for a suit with no sheet. */
  selected: Nullable<SpecSheetEntry>;
};

/** @description The spec sheet the URL's `?spec=` picks, among all the suit's sheets. */
export function useSpecSheetSelection(
  sheets: readonly MobileSuitSpecSheetEntity[],
): SpecSheetSelection {
  const [searchParams] = useSearchParams();
  const entries = specSheetEntries(sheets);
  const index = selectSpecSheetIndex({ entries, spec: searchParams.get(SPEC_PARAM) });
  return { entries, index, selected: entries[index] ?? null };
}
