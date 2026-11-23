import { describe, expect, it, vi } from 'vitest';

import { SHIFT_LS_KEY } from '@/constants';
import { SET_SHIFT } from '@/store/actionTypes';

import { hydrateShift, setShift } from './actions';

describe('preferences actions', () => {
  describe('setShift', () => {
    it('applies, stores and dispatches the shift', () => {
      const dispatch = vi.fn();

      setShift({ dispatch, shift: 'day' });

      expect(document.documentElement).toHaveAttribute('data-shift', 'day');
      expect(localStorage.getItem(SHIFT_LS_KEY)).toBe('"day"');
      expect(dispatch).toHaveBeenCalledWith({
        type: SET_SHIFT,
        payload: { preferences: { shift: 'day' } },
      });
    });
  });

  describe('hydrateShift', () => {
    it('dispatches and applies the stored shift without writing storage', () => {
      localStorage.setItem(SHIFT_LS_KEY, JSON.stringify('night'));
      const setItem = vi.spyOn(Storage.prototype, 'setItem');
      const dispatch = vi.fn();

      hydrateShift({ dispatch });

      expect(document.documentElement).toHaveAttribute('data-shift', 'night');
      expect(setItem).not.toHaveBeenCalled();
      expect(dispatch).toHaveBeenCalledWith({
        type: SET_SHIFT,
        payload: { preferences: { shift: 'night' } },
      });
    });
  });
});
