import { describe, expect, it, vi } from 'vitest';

import { SHIFT_LS_KEY, SHIFTS } from '@/constants';

import indexHTML from '../../index.html?raw';

/** @description The inline script in `index.html` that applies the stored shift. */
function readShiftScript(): string {
  const shiftScript = /<script>([\s\S]*?)<\/script>/.exec(indexHTML)?.[1];
  if (shiftScript == null)
    throw new Error('[readShiftScript] : index.html has no inline script');
  return shiftScript;
}

function runShiftScript(): void {
  // NOTE: runs index.html's own script, as the browser would.
  // oxlint-disable-next-line typescript/no-implied-eval
  new Function(readShiftScript())();
}

describe("index.html's shift script", () => {
  it.each(SHIFTS)('applies a stored %s shift as SHIFT_LS_KEY holds it', (shift) => {
    localStorage.setItem(SHIFT_LS_KEY, JSON.stringify(shift));

    runShiftScript();

    if (shift === 'auto') {
      expect(document.documentElement).not.toHaveAttribute('data-shift');
    } else {
      expect(document.documentElement).toHaveAttribute('data-shift', shift);
    }
  });

  it.each([
    ['nothing is stored', null],
    ['the value is not JSON', 'night'],
    ['the value is not a shift', JSON.stringify('dusk')],
  ])('leaves the OS scheme when %s', (_reason, storedValue) => {
    if (storedValue != null) localStorage.setItem(SHIFT_LS_KEY, storedValue);

    runShiftScript();

    expect(document.documentElement).not.toHaveAttribute('data-shift');
  });

  it('does not throw when localStorage throws', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new DOMException('Storage is disabled', 'SecurityError');
    });

    expect(runShiftScript).not.toThrow();
    expect(document.documentElement).not.toHaveAttribute('data-shift');
  });
});
