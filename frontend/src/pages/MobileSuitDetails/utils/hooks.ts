import { useSearchParams } from 'react-router';

import type { MobileSuitSpecSheetEntity } from '@/api';
import type { Nullable } from '@/types';

import {
  selectSpecSheetIndex,
  SPEC_PARAM,
  specSheetKeys,
  specSheetLabels,
} from './specSheets';

export type SelectedSpecSheet = {
  index: number;
  keys: string[];
  labels: string[];
  /** @description The selected sheet, or `null` for a suit with none. */
  sheet: Nullable<MobileSuitSpecSheetEntity>;
};

/** @description The spec sheet the URL's `?spec=` picks, with every sheet's key and label. */
export function useSelectedSpecSheet(
  sheets: readonly MobileSuitSpecSheetEntity[],
): SelectedSpecSheet {
  const [searchParams] = useSearchParams();
  const keys = specSheetKeys(sheets);
  const index = selectSpecSheetIndex({ keys, spec: searchParams.get(SPEC_PARAM) });
  return { index, keys, labels: specSheetLabels(sheets), sheet: sheets[index] ?? null };
}
