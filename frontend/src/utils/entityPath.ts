import type { EntityKind } from '@/types';

/** @description Each entity kind's list route; its detail route adds `/:<kind>Slug`. */
export const ENTITY_LIST_PATHS: Record<EntityKind, string> = {
  character: '/characters',
  mechanicalDesigner: '/mechanical-designers',
  mobileSuit: '/mobile-suits',
  organization: '/organizations',
  work: '/works',
};

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
  const listPath = ENTITY_LIST_PATHS[kind];
  return slug == null ? listPath : `${listPath}/${encodeURIComponent(slug)}`;
}
