import { describe, expect, it } from 'vitest';

import { mockSources, mockWikidataSource } from '@/__mocks__/catalogMocks';
import { mockMobileSuitDetails, mockRx782Gundam } from '@/__mocks__/mobileSuitMocks';

import { collectCitations } from './citations';

describe('collectCitations', () => {
  it('lists the spec sheets first, as the infobox names its sheet before the credits', () => {
    const suit = mockMobileSuitDetails[mockRx782Gundam.slug]!;
    const citations = collectCitations({
      ...suit,
      appearances: suit.appearances.map((appearance) => ({
        ...appearance,
        source: mockSources.mobileSuitGundam,
      })),
      designers: suit.designers.map((credit) => ({
        ...credit,
        source: mockSources.amuroRay,
      })),
      relations: [],
      spec_sheets: suit.spec_sheets.map((sheet) => ({
        ...sheet,
        source: mockWikidataSource,
      })),
    });

    expect(citations.slice(0, suit.spec_sheets.length)).toEqual(
      suit.spec_sheets.map(() => mockWikidataSource),
    );
    expect(citations[suit.spec_sheets.length]).toEqual(mockSources.amuroRay);
    expect(citations.at(-1)).toEqual(mockSources.mobileSuitGundam);
  });
});
