import { ENTITY_KINDS } from '@/constants';
import type { EntityKind } from '@/types';

/**
 * @description The path to an entity's page, or to its kind's list without a `slug`.
 * @example
 * ```ts
 * entityPath({ kind: 'mobileSuit', slug: 'rx-78-2-gundam' }); // '/mobile-suits/rx-78-2-gundam'
 * entityPath({ kind: 'work' }); // '/works'
 * ```
 */
export function entityPath({
  kind,
  slug,
}: {
  kind: EntityKind;
  slug?: string;
}): string {
  const { listPath } = ENTITY_KINDS[kind];
  return slug == null ? listPath : `${listPath}/${encodeURIComponent(slug)}`;
}
