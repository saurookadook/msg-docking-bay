import type { Nullable } from '@/types';

/**
 * @description The continuities an entity's appearances fall in, once each, in the order
 * of their works, for a header's class line: `Universal Century · Cosmic Era`.
 * @returns `null` when no appearance has a continuity
 */
export function continuityNames(
  appearances: readonly { work: { continuity: Nullable<{ name: string }> } }[],
): Nullable<string> {
  const names = appearances.flatMap(({ work }) =>
    work.continuity == null ? [] : [work.continuity.name],
  );
  return names.length === 0 ? null : [...new Set(names)].join(' · ');
}
