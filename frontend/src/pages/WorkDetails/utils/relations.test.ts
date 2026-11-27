import { describe, expect, it } from 'vitest';

import { mockNow, mockSources } from '@/__mocks__/catalogMocks';
import { mockMobileSuitGundamI, mockTheOrigin } from '@/__mocks__/workMocks';
import type { RelatedWorkEntity } from '@/api';

import { groupRelations } from './relations';

function relation({
  direction,
  relation_type,
  work = mockMobileSuitGundamI,
}: {
  direction: RelatedWorkEntity['direction'];
  relation_type: RelatedWorkEntity['relation_type'];
  work?: RelatedWorkEntity['work'];
}): RelatedWorkEntity {
  return {
    created_at: mockNow,
    direction,
    relation_type,
    source: mockSources.mobileSuitGundamI,
    work,
  };
}

describe('groupRelations', () => {
  it.each([
    ['sequel_of', 'outgoing', 'Sequel to'],
    ['sequel_of', 'incoming', 'Sequels'],
    ['compilation_of', 'outgoing', 'Compilation of'],
    ['compilation_of', 'incoming', 'Compiled in'],
    ['adaptation_of', 'outgoing', 'Adaptation of'],
    ['adaptation_of', 'incoming', 'Adaptations'],
    ['remake_of', 'outgoing', 'Remake of'],
    ['remake_of', 'incoming', 'Remakes'],
    ['side_story_of', 'outgoing', 'Side story of'],
    ['side_story_of', 'incoming', 'Side stories'],
  ] as const)('labels a %s %s relation %o', (type, direction, label) => {
    expect(
      groupRelations([relation({ direction, relation_type: type })]).map(
        (group) => group.label,
      ),
    ).toEqual([label]);
  });

  it('puts what the work is before what came of it, and groups each type', () => {
    const groups = groupRelations([
      relation({ direction: 'incoming', relation_type: 'compilation_of' }),
      relation({ direction: 'outgoing', relation_type: 'sequel_of' }),
      relation({
        direction: 'incoming',
        relation_type: 'compilation_of',
        work: mockTheOrigin,
      }),
    ]);

    expect(groups.map(({ key, relations }) => [key, relations.length])).toEqual([
      ['sequel_of-outgoing', 1],
      ['compilation_of-incoming', 2],
    ]);
  });

  it('gives no group for a work with no relations', () => {
    expect(groupRelations([])).toEqual([]);
  });
});
