import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';

import { SHIFT_LS_KEY } from '@/constants';
import { AppStoreProvider, initialAppState } from '@/store';
import type { Shift } from '@/types';

import { ShiftToggle } from '.';

function renderShiftToggle(shift: Shift = 'auto') {
  return render(
    <AppStoreProvider initialState={{ ...initialAppState, preferences: { shift } }}>
      <ShiftToggle />
    </AppStoreProvider>,
  );
}

describe('ShiftToggle', () => {
  it('offers the three shifts and checks the current one', () => {
    renderShiftToggle('night');

    const shiftGroup = screen.getByRole('group', { name: 'Shift' });
    expect(shiftGroup).toBeVisible();
    expect(screen.getByRole('radio', { name: 'Auto' })).not.toBeChecked();
    expect(screen.getByRole('radio', { name: 'Day' })).not.toBeChecked();
    expect(screen.getByRole('radio', { name: 'Night' })).toBeChecked();
  });

  it('switches the shift, applies it to the page and stores it', async () => {
    const user = userEvent.setup();
    renderShiftToggle();

    await user.click(screen.getByRole('radio', { name: 'Day' }));

    expect(screen.getByRole('radio', { name: 'Day' })).toBeChecked();
    expect(document.documentElement).toHaveAttribute('data-shift', 'day');
    expect(localStorage.getItem(SHIFT_LS_KEY)).toBe('"day"');
  });

  it('goes back to the OS scheme on Auto', async () => {
    const user = userEvent.setup();
    renderShiftToggle('night');
    document.documentElement.dataset.shift = 'night';

    await user.click(screen.getByRole('radio', { name: 'Auto' }));

    expect(document.documentElement).not.toHaveAttribute('data-shift');
  });
});
