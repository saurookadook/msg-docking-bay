import { SET_SHIFT } from '@/store/actionTypes';
import type { BaseAction } from '@/store/types';
import type { Shift } from '@/types';
import { applyShift, readStoredShift, storeShift } from '@/utils';

/** @description Switches the deck to `shift`: applies it, stores it, and records it. */
export function setShift({ dispatch, shift }: BaseAction & { shift: Shift }): void {
  applyShift(shift);
  storeShift(shift);
  return dispatch({ type: SET_SHIFT, payload: { preferences: { shift } } });
}

/**
 * @description Loads the stored shift into the store after mount (REACT-14).
 * @note It does not write storage back; it re-applies the shift only so the page and
 * the store agree even when `index.html`'s script didn't run.
 */
export function hydrateShift({ dispatch }: BaseAction): void {
  const storedShift = readStoredShift();
  applyShift(storedShift);
  return dispatch({
    type: SET_SHIFT,
    payload: { preferences: { shift: storedShift } },
  });
}
