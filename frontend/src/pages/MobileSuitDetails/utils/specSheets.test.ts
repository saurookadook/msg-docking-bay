import { describe, expect, it } from 'vitest';

import { mockWikidataSource } from '@/__mocks__/catalogMocks';
import { mockMobileSuitDetails, mockRx782Gundam } from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitSpecSheetEntity } from '@/api';

import { selectSpecSheetIndex, specSheetEntries } from './specSheets';

const [baseSheet, magnetCoatingSheet] =
  mockMobileSuitDetails[mockRx782Gundam.slug]!.spec_sheets;

function sheet(values: Partial<MobileSuitSpecSheetEntity>): MobileSuitSpecSheetEntity {
  return { ...baseSheet!, ...values };
}

/** @description The `?spec=` keys and tab labels the sheets get. */
function namesOf(sheets: MobileSuitSpecSheetEntity[]) {
  const entries = specSheetEntries(sheets);
  return {
    keys: entries.map(({ key }) => key),
    labels: entries.map(({ label }) => label),
  };
}

describe('specSheets', () => {
  describe('specSheetEntries', () => {
    it('names the base sheet and each configuration', () => {
      const sheets = [baseSheet!, magnetCoatingSheet!];

      expect(namesOf(sheets).keys).toEqual(['base', 'magnet-coating']);
      expect(namesOf(sheets).labels).toEqual(['Base spec', 'Magnet Coating']);
    });

    it('adds the source kind when two sheets share a name', () => {
      const sheets = [baseSheet!, sheet({ source: mockWikidataSource })];

      expect(namesOf(sheets).keys).toEqual(['base-gundam-wiki', 'base-wikidata']);
      expect(namesOf(sheets).labels).toEqual([
        'Base spec (Gundam Wiki)',
        'Base spec (Wikidata)',
      ]);
    });

    it('adds the place when the source kind still collides', () => {
      const sheets = [
        sheet({ configuration: 'G-Armor' }),
        sheet({ configuration: 'G Armor' }),
      ];

      expect(namesOf(sheets).keys).toEqual([
        'g-armor-gundam-wiki-1',
        'g-armor-gundam-wiki-2',
      ]);
      expect(namesOf(sheets).labels).toEqual(['G-Armor', 'G Armor']);
    });

    it('labels two same-named sheets from one kind of source by place', () => {
      expect(namesOf([baseSheet!, sheet({})]).labels).toEqual([
        'Base spec (Gundam Wiki) 1',
        'Base spec (Gundam Wiki) 2',
      ]);
    });

    it('keys a configuration with no ASCII letters by its place', () => {
      expect(namesOf([baseSheet!, sheet({ configuration: '強化型' })]).keys).toEqual([
        'base',
        'sheet-2',
      ]);
    });
  });

  describe('selectSpecSheetIndex', () => {
    it.each([
      ['magnet-coating', 1],
      [null, 0],
      ['unknown', 0],
    ])('picks %o as sheet %i', (spec, index) => {
      const entries = specSheetEntries([baseSheet!, magnetCoatingSheet!]);
      expect(selectSpecSheetIndex({ entries, spec })).toBe(index);
    });
  });
});
