import { describe, expect, it } from 'vitest';

import { mockSources } from '@/__mocks__/catalogMocks';
import { mockMobileSuits } from '@/__mocks__/mobileSuitMocks';
import type {
  MobileSuitRelationType,
  RelatedMobileSuitEntity,
  RelationDirection,
} from '@/api';

import { buildLineage } from './lineage';

function relation(
  relation_type: MobileSuitRelationType,
  direction: RelationDirection,
  index = 0,
): RelatedMobileSuitEntity {
  return {
    created_at: '2026-11-21T00:00:00Z',
    direction,
    mobile_suit: mockMobileSuits[index]!,
    relation_type,
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
      const related = relation(type, direction);

      expect(buildLineage([related])[tier]).toEqual([{ label, relations: [related] }]);
    });

    it('merges alternate versions from both directions into one group', () => {
      const outgoing = relation('alternate_version_of', 'outgoing', 1);
      const incoming = relation('alternate_version_of', 'incoming', 2);

      expect(buildLineage([incoming, outgoing]).alternates).toEqual([
        { label: 'Alternate versions', relations: [outgoing, incoming] },
      ]);
    });

    it('orders groups by wording and leaves empty tiers empty', () => {
      const variant = relation('variant_of', 'outgoing');
      const developedFrom = relation('developed_from', 'outgoing', 1);

      expect(buildLineage([variant, developedFrom])).toEqual({
        alternates: [],
        ancestors: [
          { label: 'Developed from', relations: [developedFrom] },
          { label: 'Variant of', relations: [variant] },
        ],
        descendants: [],
      });
    });
  });
});
