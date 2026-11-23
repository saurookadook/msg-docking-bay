import { describe, expect, it, vi } from 'vitest';

import { SHIFT_LS_KEY } from '@/constants';

import { applyShift, readStoredShift, storeShift } from './shiftStorage';

describe('shiftStorage', () => {
  describe('readStoredShift', () => {
    it('reads the stored shift', () => {
      localStorage.setItem(SHIFT_LS_KEY, JSON.stringify('day'));

      expect(readStoredShift()).toBe('day');
    });

    it.each([
      ['nothing is stored', null],
      ['the value is not JSON', 'night'],
      ['the value is not a shift', JSON.stringify('dusk')],
    ])('falls back to auto when %s', (_reason, storedValue) => {
      if (storedValue != null) localStorage.setItem(SHIFT_LS_KEY, storedValue);

      expect(readStoredShift()).toBe('auto');
    });

    it('falls back to auto when localStorage throws', () => {
      vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
        throw new DOMException('Storage is disabled', 'SecurityError');
      });

      expect(readStoredShift()).toBe('auto');
    });
  });

  describe('storeShift', () => {
    it('stores the shift as JSON', () => {
      storeShift('night');

      expect(localStorage.getItem(SHIFT_LS_KEY)).toBe('"night"');
    });

    it('does not throw when localStorage throws', () => {
      vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw new DOMException('Quota exceeded', 'QuotaExceededError');
      });

      expect(() => storeShift('day')).not.toThrow();
    });
  });

  describe('applyShift', () => {
    it('sets data-shift on <html> for day and night', () => {
      applyShift('night');

      expect(document.documentElement).toHaveAttribute('data-shift', 'night');
    });

    it('removes data-shift for auto, so the OS scheme applies', () => {
      applyShift('day');
      applyShift('auto');

      expect(document.documentElement).not.toHaveAttribute('data-shift');
    });
  });
});
