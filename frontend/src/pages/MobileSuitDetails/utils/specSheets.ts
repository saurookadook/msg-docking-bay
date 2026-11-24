import type { MobileSuitSpecSheetEntity, SourceKind } from '@/api';
import { SOURCE_KIND_LABELS } from '@/constants';
import type { Nullable } from '@/types';
import { slugify } from '@/utils';

/** @description The `?spec=` param that picks a suit's spec sheet. */
export const SPEC_PARAM = 'spec';

/** @description A spec sheet's name: its configuration, or "Base spec". */
const BASE_SPEC_LABEL = 'Base spec';

/** @description A spec sheet with the names the page shows and links it by. */
export type SpecSheetEntry = {
  /** @description Its `?spec=` value, such as `magnet-coating`. */
  key: string;
  /** @description Its tab label, such as "Magnet Coating". */
  label: string;
  sheet: MobileSuitSpecSheetEntity;
};

/**
 * @description Makes one name of each entry unique: a name two entries share gets its
 * sheet's source kind added, and the entry's place if that still collides.
 */
function withUniqueNames({
  entries,
  field,
  withPlace,
  withSource,
}: {
  entries: SpecSheetEntry[];
  field: 'key' | 'label';
  withPlace: (args: { name: string; place: number }) => string;
  withSource: (args: { kind: SourceKind; name: string }) => string;
}): SpecSheetEntry[] {
  const isShared = ({
    entry,
    list,
  }: {
    entry: SpecSheetEntry;
    list: SpecSheetEntry[];
  }) => list.filter((other) => other[field] === entry[field]).length > 1;
  const sourced = entries.map((entry) =>
    isShared({ entry, list: entries })
      ? {
          ...entry,
          [field]: withSource({ kind: entry.sheet.source.kind, name: entry[field] }),
        }
      : entry,
  );
  return sourced.map((entry, index) =>
    isShared({ entry, list: sourced })
      ? { ...entry, [field]: withPlace({ name: entry[field], place: index + 1 }) }
      : entry,
  );
}

/**
 * @description Each sheet, in the sheets' order, with its `?spec=` key (its slugified
 * configuration, or `base`) and its tab label (its configuration, or "Base spec").
 * @note A configuration with no ASCII letters or digits is keyed `sheet-<place>`.
 */
export function specSheetEntries(
  sheets: readonly MobileSuitSpecSheetEntity[],
): SpecSheetEntry[] {
  const named = sheets.map((sheet, index) => ({
    key:
      sheet.configuration == null
        ? 'base'
        : slugify(sheet.configuration) || `sheet-${index + 1}`,
    label: sheet.configuration ?? BASE_SPEC_LABEL,
    sheet,
  }));
  const keyed = withUniqueNames({
    entries: named,
    field: 'key',
    withPlace: ({ name, place }) => `${name}-${place}`,
    withSource: ({ kind, name }) => `${name}-${slugify(SOURCE_KIND_LABELS[kind])}`,
  });
  return withUniqueNames({
    entries: keyed,
    field: 'label',
    withPlace: ({ name, place }) => `${name} ${place}`,
    withSource: ({ kind, name }) => `${name} (${SOURCE_KIND_LABELS[kind]})`,
  });
}

/**
 * @description The place of the entry `spec` names.
 * @returns `0` (the first sheet) without a `spec`, or for one no entry has
 */
export function selectSpecSheetIndex({
  entries,
  spec,
}: {
  entries: readonly SpecSheetEntry[];
  spec: Nullable<string>;
}): number {
  const index = entries.findIndex(({ key }) => key === spec);
  return index === -1 ? 0 : index;
}
