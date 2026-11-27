import { describe, expect, it } from 'vitest';

import { mockNow, mockSources } from '@/__mocks__/catalogMocks';
import { mockMobileSuits } from '@/__mocks__/mobileSuitMocks';
import type {
  MobileSuitRelationType,
  RelatedMobileSuitEntity,
  RelationDirection,
} from '@/api';

import { buildLineage } from './lineage';

/** @description A relation to one of the mock suits, picked by its place in the list. */
function relation({
  direction,
  index = 0,
  type,
}: {
  direction: RelationDirection;
  index?: number;
  type: MobileSuitRelationType;
}): RelatedMobileSuitEntity {
  return {
    created_at: mockNow,
    direction,
    mobile_suit: mockMobileSuits[index]!,
    relation_type: type,
    source: mockSources.rx782Gundam,
  };
}

describe('lineage', () => {
  describe('buildLineage', () => {
    it.each([
      ['developed_from', 'outgoing', 'ancestors', 'Developed from'],
      ['developed_from', 'incoming', 'descendants', 'Developed into'],
      ['upgrade_of', 'outgoing', 'ancestors', 'Upgrade of'],
      ['upgrade_of', 'incoming', 'descendants', 'Upgraded into'],
      ['variant_of', 'outgoing', 'ancestors', 'Variant of'],
      ['variant_of', 'incoming', 'descendants', 'Variants'],
      ['alternate_version_of', 'outgoing', 'alternates', 'Alternate versions'],
      ['alternate_version_of', 'incoming', 'alternates', 'Alternate versions'],
    ] as const)('puts %s %s under %s as "%s"', (type, direction, tier, label) => {
      const related = relation({ direction, type });

      expect(buildLineage([related])[tier]).toEqual([
        { key: expect.any(String), label, relations: [related] },
      ]);
    });

    it('merges alternate versions from both directions into one group', () => {
      const outgoing = relation({
        direction: 'outgoing',
        index: 1,
        type: 'alternate_version_of',
      });
      const incoming = relation({
        direction: 'incoming',
        index: 2,
        type: 'alternate_version_of',
      });

      expect(buildLineage([incoming, outgoing]).alternates).toEqual([
        {
          key: 'alternate_versions',
          label: 'Alternate versions',
          relations: [outgoing, incoming],
        },
      ]);
    });

    it('orders groups by wording and leaves empty tiers empty', () => {
      const variant = relation({ direction: 'outgoing', type: 'variant_of' });
      const developedFrom = relation({
        direction: 'outgoing',
        index: 1,
        type: 'developed_from',
      });

      expect(buildLineage([variant, developedFrom])).toEqual({
        alternates: [],
        ancestors: [
          {
            key: 'developed_from-outgoing',
            label: 'Developed from',
            relations: [developedFrom],
          },
          { key: 'variant_of-outgoing', label: 'Variant of', relations: [variant] },
        ],
        descendants: [],
      });
    });
  });
});
