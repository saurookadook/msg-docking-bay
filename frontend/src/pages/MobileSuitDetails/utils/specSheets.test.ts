import { describe, expect, it } from 'vitest';

import { mockWikidataSource } from '@/__mocks__/catalogMocks';
import { mockMobileSuitDetails, mockRx782Gundam } from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitSpecSheetEntity } from '@/api';

import { selectSpecSheetIndex, specSheetKeys, specSheetLabels } from './specSheets';

const [baseSheet, magnetCoatingSheet] =
  mockMobileSuitDetails[mockRx782Gundam.slug]!.spec_sheets;

function sheet(values: Partial<MobileSuitSpecSheetEntity>): MobileSuitSpecSheetEntity {
  return { ...baseSheet!, ...values };
}

describe('specSheets', () => {
  describe('specSheetKeys and specSheetLabels', () => {
    it('names the base sheet and each configuration', () => {
      const sheets = [baseSheet!, magnetCoatingSheet!];

      expect(specSheetKeys(sheets)).toEqual(['base', 'magnet-coating']);
      expect(specSheetLabels(sheets)).toEqual(['Base spec', 'Magnet Coating']);
    });

    it('adds the source kind when two sheets share a name', () => {
      const sheets = [baseSheet!, sheet({ source: mockWikidataSource })];

      expect(specSheetKeys(sheets)).toEqual(['base-gundam-wiki', 'base-wikidata']);
      expect(specSheetLabels(sheets)).toEqual([
        'Base spec (Gundam Wiki)',
        'Base spec (Wikidata)',
      ]);
    });

    it('adds the place when the source kind still collides', () => {
      const sheets = [
        sheet({ configuration: 'G-Armor' }),
        sheet({ configuration: 'G Armor' }),
      ];

      expect(specSheetKeys(sheets)).toEqual([
        'g-armor-gundam-wiki-1',
        'g-armor-gundam-wiki-2',
      ]);
      expect(specSheetLabels(sheets)).toEqual(['G-Armor', 'G Armor']);
    });

    it('labels two same-named sheets from one kind of source by place', () => {
      expect(specSheetLabels([baseSheet!, sheet({})])).toEqual([
        'Base spec (Gundam Wiki) 1',
        'Base spec (Gundam Wiki) 2',
      ]);
    });

    it('keys a configuration with no ASCII letters by its place', () => {
      expect(specSheetKeys([baseSheet!, sheet({ configuration: '強化型' })])).toEqual([
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
      expect(selectSpecSheetIndex({ keys: ['base', 'magnet-coating'], spec })).toBe(
        index,
      );
    });
  });
});
