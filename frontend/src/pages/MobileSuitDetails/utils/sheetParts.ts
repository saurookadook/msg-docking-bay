import type { MaterialUse, MobileSuitSpecSheetEntity, SpecSheetField } from '@/api';
import type { SpecPlateItem } from '@/components';
import type { Nullable } from '@/types';

import { formatMeasurement, formatQuantity, MEASUREMENTS } from './format';

/** @description One listed part, as the parts panel and the infobox show it. */
export type PartItem = {
  /** @description Its note, and how it is carried, as one muted line. */
  detail: Nullable<string>;
  key: string;
  name: string;
  /** @description Its count, such as `2 ×`, or `null` when none was given. */
  quantity: Nullable<string>;
};

/** @description Each material use's heading. */
export const MATERIAL_USE_LABELS = {
  armor: 'Armor',
  frame: 'Frame',
} as const satisfies Record<MaterialUse, string>;

// NOTE: `Object.keys` types its result as string[]; these are MATERIAL_USE_LABELS' own keys.
export const MATERIAL_USES = Object.keys(MATERIAL_USE_LABELS) as MaterialUse[];

/**
 * @description A measurement's spec plate row: its label, its value with the unit, and
 * whether the sheet took it from its base sheet.
 */
export function measurementItem({
  field,
  sheet,
}: {
  field: SpecSheetField;
  sheet: Nullable<MobileSuitSpecSheetEntity>;
}): SpecPlateItem {
  return {
    isInherited: sheet?.inherited_fields.includes(field) ?? false,
    label: MEASUREMENTS[field].label,
    value: formatMeasurement({ field, value: sheet?.[field] ?? null }),
  };
}

/** @description The sheet's materials of one use, in the API's order. */
export function materialItems({
  sheet,
  use,
}: {
  sheet: Nullable<MobileSuitSpecSheetEntity>;
  use: MaterialUse;
}): PartItem[] {
  return (sheet?.materials ?? [])
    .filter(({ material_use }) => material_use === use)
    .map(({ material, note }) => ({
      detail: note,
      key: material.slug,
      name: material.name,
      quantity: null,
    }));
}

/** @description The sheet's powerplants, each with its count. */
export function powerplantItems(
  sheet: Nullable<MobileSuitSpecSheetEntity>,
): PartItem[] {
  return (sheet?.powerplants ?? []).map((listing) => ({
    detail: listing.note,
    key: listing.powerplant.slug,
    name: listing.powerplant.name,
    quantity: formatQuantity(listing),
  }));
}

/** @description A part as one line of text: its count, then its name. */
export function partText({
  name,
  quantity,
}: Pick<PartItem, 'name' | 'quantity'>): string {
  return quantity == null ? name : `${quantity} ${name}`;
}
