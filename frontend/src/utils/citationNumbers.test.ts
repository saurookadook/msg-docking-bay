import { describe, expect, it } from 'vitest';

import { mockSources, mockWikidataSource } from '@/__mocks__/catalogMocks';

import { citationKey, numberCitations } from './citationNumbers';

describe('citationNumbers', () => {
  describe('numberCitations', () => {
    it('numbers each distinct source once, in the order first seen', () => {
      const { citations, numberOf } = numberCitations([
        mockSources.rx782Gundam,
        mockWikidataSource,
        { ...mockSources.rx782Gundam },
      ]);

      expect(citations).toEqual([mockSources.rx782Gundam, mockWikidataSource]);
      expect(numberOf({ ...mockSources.rx782Gundam })).toBe(1);
      expect(numberOf(mockWikidataSource)).toBe(2);
    });

    it('keeps two revisions of one page apart', () => {
      const olderRevision = { ...mockSources.rx782Gundam, revision_id: 1 };

      const { citations, numberOf } = numberCitations([
        mockSources.rx782Gundam,
        olderRevision,
      ]);

      expect(citations).toHaveLength(2);
      expect(numberOf(olderRevision)).toBe(2);
    });

    it('throws for a source it was not given', () => {
      const { numberOf } = numberCitations([mockSources.rx782Gundam]);

      expect(() => numberOf(mockWikidataSource)).toThrow(
        '[numberCitations] : no number for https://www.wikidata.org/wiki/Q1',
      );
    });
  });

  describe('citationKey', () => {
    it('tells a page with no revision apart from one with a revision', () => {
      expect(citationKey(mockWikidataSource)).toBe(
        'wikidata_item|https://www.wikidata.org/wiki/Q1|',
      );
      expect(citationKey(mockSources.rx782Gundam)).toBe(
        'fandom_page|https://gundam.fandom.com/wiki/RX-78-2_Gundam|707889',
      );
    });
  });
});
