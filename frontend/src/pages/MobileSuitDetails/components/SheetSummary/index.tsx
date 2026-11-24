import type { MobileSuitSpecSheetEntity } from '@/api';
import { SpecPlate, type SpecPlateItem } from '@/components';
import type { Nullable } from '@/types';

import type { Cite } from '../../utils/citations';
import { entryList, type Entry } from '../../utils/entryList';
import { lineupHeight } from '../../utils/lineup';
import {
  MATERIAL_USE_LABELS,
  MATERIAL_USES,
  materialItems,
  measurementItem,
  partText,
  powerplantItems,
  type PartItem,
} from '../../utils/sheetParts';
import type { SpecSheetEntry } from '../../utils/specSheets';

import './styles.css';

/** @description The sheet's headline numbers and parts. */
function summaryItems(sheet: Nullable<MobileSuitSpecSheetEntity>): SpecPlateItem[] {
  const partsInherited = (kind: MobileSuitSpecSheetEntity['inherited_parts'][number]) =>
    sheet?.inherited_parts.includes(kind) ?? false;
  const partList = (items: PartItem[]) =>
    entryList(items.map((item): Entry => ({ content: partText(item), key: item.key })));

  return [
    measurementItem({ field: lineupHeight(sheet)?.field ?? 'overall_height_m', sheet }),
    measurementItem({ field: 'gross_weight_kg', sheet }),
    {
      isInherited: partsInherited('powerplants'),
      label: 'Powerplant',
      value: partList(powerplantItems(sheet)),
    },
    ...MATERIAL_USES.map((use) => ({
      isInherited: partsInherited('materials'),
      label: MATERIAL_USE_LABELS[use],
      value: partList(materialItems({ sheet, use })),
    })),
    // NOTE: a part kind is inherited whole, so a row with nothing of its own use stays pending.
  ].map((item) => ({
    ...item,
    isInherited: item.isInherited === true && item.value != null,
  }));
}

export type SheetSummaryProps = {
  cite: Cite;
  /** @description The sheet the tabs have selected, or `null` for a suit with none. */
  selected: Nullable<SpecSheetEntry>;
};

/**
 * @description The selected spec sheet's name and headline numbers: height, gross weight,
 * powerplants and materials.
 */
export function SheetSummary({ cite, selected }: SheetSummaryProps) {
  return (
    <>
      {selected != null && (
        <p className="sheet-summary-name stencil-label">
          {selected.label}
          {cite(selected.sheet.source)}
        </p>
      )}
      <SpecPlate
        aria-label="Spec summary"
        items={summaryItems(selected?.sheet ?? null)}
      />
    </>
  );
}
