import { SHIFT_LS_KEY, SHIFTS } from '@/constants';
import type { Shift } from '@/types';
import { safeParseJSON, sharedLog } from '@/utils';

const logger = sharedLog.getLogger('preferencesStorage');

/** @description Narrows a stored value to a `Shift`. */
function isShift(value: unknown): value is Shift {
  return SHIFTS.some((candidate) => candidate === value);
}

/**
 * @description Reads the shift stored under `SHIFT_LS_KEY`.
 * @returns the stored shift, or `'auto'` when none is stored, the value is not a shift,
 * or `localStorage` throws (storage disabled)
 */
export function readStoredShift(): Shift {
  try {
    const storedShift = safeParseJSON(localStorage.getItem(SHIFT_LS_KEY) ?? '');
    return isShift(storedShift) ? storedShift : 'auto';
  } catch {
    return 'auto';
  }
}

/**
 * @description Stores `shift` under `SHIFT_LS_KEY`, so the next visit starts on it.
 * @note A failed write (storage disabled or full) is logged, not thrown: the shift
 * still applies for this visit.
 */
export function storeShift(shift: Shift): void {
  try {
    localStorage.setItem(SHIFT_LS_KEY, JSON.stringify(shift));
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logger.error('[storeShift] : Could not store the shift', shift, err);
  }
}

/**
 * @description Applies `shift` to the page as `<html data-shift>`, which `index.css`
 * reads to pick the color scheme. `auto` removes the attribute.
 */
export function applyShift(shift: Shift): void {
  if (shift === 'auto') {
    delete document.documentElement.dataset.shift;
    return;
  }
  document.documentElement.dataset.shift = shift;
}
