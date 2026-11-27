import { describe, expect, it } from 'vitest';

import { mockSources } from '@/__mocks__/catalogMocks';
import { findCharacterMock } from '@/__mocks__/characterMocks';

import { collectCitations } from './citations';

describe('collectCitations', () => {
  it('lists the qualified units before the appearances', () => {
    const character = findCharacterMock('amuro-ray')!;
    const citations = collectCitations({
      ...character,
      appearances: character.appearances.map((appearance) => ({
        ...appearance,
        source: mockSources.mobileSuitGundam,
      })),
    });

    expect(citations).toEqual([
      ...character.piloted_mobile_suits.map(({ source }) => source),
      ...character.appearances.map(() => mockSources.mobileSuitGundam),
    ]);
  });
});
