import { describe, expect, it } from 'vitest';

import { mockRx782GundamBaseSheet } from '@/__mocks__/mobileSuitMocks';

import { lineupHeight, lineupLayout } from './lineup';

describe('lineup', () => {
  describe('lineupHeight', () => {
    it('prefers the overall height', () => {
      expect(
        lineupHeight({ ...mockRx782GundamBaseSheet, overall_height_m: 19.5 }),
      ).toEqual({
        field: 'overall_height_m',
        metres: 19.5,
      });
    });

    it('falls back to the head height', () => {
      expect(lineupHeight(mockRx782GundamBaseSheet)).toEqual({
        field: 'head_height_m',
        metres: 18,
      });
    });

    it('gives null with neither, or no sheet', () => {
      expect(
        lineupHeight({ ...mockRx782GundamBaseSheet, head_height_m: null }),
      ).toBeNull();
      expect(lineupHeight(null)).toBeNull();
    });
  });

  describe('lineupLayout', () => {
    it('stands the figures side by side, in order, on one ground line', () => {
      const { figures, groundY } = lineupLayout(18);

      expect(figures.map(({ kind, metres }) => [kind, metres])).toEqual([
        ['human', 1.7],
        ['reference', 18],
        ['suit', 18],
      ]);
      for (const [left, right] of [
        [figures[0]!, figures[1]!],
        [figures[1]!, figures[2]!],
      ]) {
        expect(left.x + left.width).toBeLessThan(right.x);
      }
      expect(groundY).toBeGreaterThan(18);
    });

    it('makes room for a suit taller than the reference frame', () => {
      const tall = lineupLayout(40);
      const short = lineupLayout(10);

      expect(tall.groundY).toBeGreaterThan(40);
      expect(short.groundY).toBe(lineupLayout(18).groundY);
      expect(tall.viewBox).toMatch(/^0 0 [\d.]+ [\d.]+$/);
    });
  });
});
