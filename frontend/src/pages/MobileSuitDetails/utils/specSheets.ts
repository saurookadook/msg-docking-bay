import type { MobileSuitSpecSheetEntity, SourceKind } from '@/api';
import { SOURCE_KIND_LABELS } from '@/constants';
import { slugify } from '@/utils';

/** @description The `?spec=` param that picks a suit's spec sheet. */
export const SPEC_PARAM = 'spec';

/** @description A spec sheet's name: its configuration, or "Base spec". */
const BASE_SPEC_LABEL = 'Base spec';

/**
 * @description Makes each name unique: a name two sheets share gets its sheet's source
 * kind added, and the sheet's place if that still collides.
 */
function disambiguate({
  names,
  sheets,
  withSource,
  withPlace,
}: {
  names: string[];
  sheets: readonly MobileSuitSpecSheetEntity[];
  withSource: (name: string, kind: SourceKind) => string;
  withPlace: (name: string, place: number) => string;
}): string[] {
  const countOf = (list: string[], name: string) =>
    list.filter((other) => other === name).length;
  const sourced = names.map((name, index) =>
    countOf(names, name) > 1 ? withSource(name, sheets[index]!.source.kind) : name,
  );
  return sourced.map((name, index) =>
    countOf(sourced, name) > 1 ? withPlace(name, index + 1) : name,
  );
}

/**
 * @description Each sheet's `?spec=` value, in the sheets' order: its slugified
 * configuration, or `base`.
 * @note A configuration with no ASCII letters or digits is `sheet-<place>`.
 */
export function specSheetKeys(sheets: readonly MobileSuitSpecSheetEntity[]): string[] {
  return disambiguate({
    names: sheets.map(({ configuration }, index) => {
      if (configuration == null) return 'base';
      return slugify(configuration) || `sheet-${index + 1}`;
    }),
    sheets,
    withPlace: (name, place) => `${name}-${place}`,
    withSource: (name, kind) => `${name}-${slugify(SOURCE_KIND_LABELS[kind])}`,
  });
}

/** @description Each sheet's tab label, in the sheets' order. */
export function specSheetLabels(
  sheets: readonly MobileSuitSpecSheetEntity[],
): string[] {
  return disambiguate({
    names: sheets.map(({ configuration }) => configuration ?? BASE_SPEC_LABEL),
    sheets,
    withPlace: (name, place) => `${name} ${place}`,
    withSource: (name, kind) => `${name} (${SOURCE_KIND_LABELS[kind]})`,
  });
}

/**
 * @description The place of the sheet `spec` names.
 * @returns `0` (the first sheet) without a `spec`, or for one no sheet has
 */
export function selectSpecSheetIndex({
  keys,
  spec,
}: {
  keys: readonly string[];
  spec: string | null;
}): number {
  const index = spec == null ? -1 : keys.indexOf(spec);
  return index === -1 ? 0 : index;
}
