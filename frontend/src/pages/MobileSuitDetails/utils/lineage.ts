import type {
  MobileSuitRelationType,
  RelatedMobileSuitEntity,
  RelationDirection,
} from '@/api';

/** @description Where a related suit sits in the dev-tree, relative to the viewed suit. */
export type LineageTier = 'ancestors' | 'alternates' | 'descendants';

/**
 * @description How each relation reads from the viewed suit's side. `outgoing` means
 * this suit is `<relation_type>` the other; `incoming` means the other is
 * `<relation_type>` this one (`catalog-read-api.md`).
 */
export const LINEAGE_WORDING = {
  developed_from: {
    outgoing: {
      group: 'developed_from-outgoing',
      label: 'Developed from',
      tier: 'ancestors',
    },
    incoming: {
      group: 'developed_from-incoming',
      label: 'Developed into',
      tier: 'descendants',
    },
  },
  upgrade_of: {
    outgoing: { group: 'upgrade_of-outgoing', label: 'Upgrade of', tier: 'ancestors' },
    incoming: {
      group: 'upgrade_of-incoming',
      label: 'Upgraded into',
      tier: 'descendants',
    },
  },
  variant_of: {
    outgoing: { group: 'variant_of-outgoing', label: 'Variant of', tier: 'ancestors' },
    incoming: { group: 'variant_of-incoming', label: 'Variants', tier: 'descendants' },
  },
  // NOTE: either way round, both are versions of one design; one group holds them.
  alternate_version_of: {
    outgoing: {
      group: 'alternate_versions',
      label: 'Alternate versions',
      tier: 'alternates',
    },
    incoming: {
      group: 'alternate_versions',
      label: 'Alternate versions',
      tier: 'alternates',
    },
  },
} as const satisfies Record<
  MobileSuitRelationType,
  Record<RelationDirection, { group: string; label: string; tier: LineageTier }>
>;

export type LineageGroup = {
  /** @description The group's identity: relations with the same key share one group. */
  key: string;
  label: string;
  relations: RelatedMobileSuitEntity[];
};

export type Lineage = Record<LineageTier, LineageGroup[]>;

/**
 * @description The suit's relations as a dev-tree: groups of related suits per tier, each
 * group labelled by its wording, in `LINEAGE_WORDING` order, relations in the API's order.
 */
export function buildLineage(relations: readonly RelatedMobileSuitEntity[]): Lineage {
  const lineage: Lineage = { ancestors: [], alternates: [], descendants: [] };
  const types = Object.keys(LINEAGE_WORDING) as MobileSuitRelationType[];
  for (const type of types) {
    for (const direction of ['outgoing', 'incoming'] as const) {
      const { group: key, label, tier } = LINEAGE_WORDING[type][direction];
      const matching = relations.filter(
        (relation) =>
          relation.relation_type === type && relation.direction === direction,
      );
      if (matching.length === 0) continue;
      const group = lineage[tier].find((existing) => existing.key === key);
      if (group == null) lineage[tier].push({ key, label, relations: matching });
      else group.relations.push(...matching);
    }
  }
  return lineage;
}
