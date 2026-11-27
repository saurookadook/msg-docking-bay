import type { RelatedWorkEntity, RelationDirection, WorkRelationType } from '@/api';

/**
 * @description How each relation reads from the viewed work's side: `outgoing` is "this
 * work is a <type> the other", `incoming` is "the other is a <type> this one".
 */
const RELATION_LABELS = {
  sequel_of: { incoming: 'Sequels', outgoing: 'Sequel to' },
  compilation_of: { incoming: 'Compiled in', outgoing: 'Compilation of' },
  adaptation_of: { incoming: 'Adaptations', outgoing: 'Adaptation of' },
  remake_of: { incoming: 'Remakes', outgoing: 'Remake of' },
  side_story_of: { incoming: 'Side stories', outgoing: 'Side story of' },
} as const satisfies Record<WorkRelationType, Record<RelationDirection, string>>;

// NOTE: `Object.keys` types its result as string[]; these are the labels' own keys.
const RELATION_TYPES = Object.keys(RELATION_LABELS) as WorkRelationType[];
const DIRECTIONS: readonly RelationDirection[] = ['outgoing', 'incoming'];

/** @description One labelled group of related works: one type, read in one direction. */
export type RelationGroup = {
  key: string;
  label: string;
  relations: RelatedWorkEntity[];
};

/**
 * @description A work's relations, grouped by type and direction: what this work is
 * first (sequel to, compilation of…), then what came of it, each in the API's order.
 * @returns only the groups that hold a relation
 */
export function groupRelations(
  relations: readonly RelatedWorkEntity[],
): RelationGroup[] {
  return DIRECTIONS.flatMap((direction) =>
    RELATION_TYPES.flatMap((relationType) => {
      const grouped = relations.filter(
        (relation) =>
          relation.direction === direction && relation.relation_type === relationType,
      );
      return grouped.length === 0
        ? []
        : [
            {
              key: `${relationType}-${direction}`,
              label: RELATION_LABELS[relationType][direction],
              relations: grouped,
            },
          ];
    }),
  );
}
