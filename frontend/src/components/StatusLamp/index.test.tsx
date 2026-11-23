import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { StatusLamp } from '.';

describe('StatusLamp', () => {
  it.each([
    ['online', 'Online'],
    ['standby', 'Standby'],
    ['busy', 'Working'],
    ['alert', 'Alert'],
    ['offline', 'Offline'],
  ] as const)('labels the %s status in words', (status, label) => {
    render(<StatusLamp status={status} />);

    expect(screen.getByText(label)).toBeVisible();
  });

  it('shows its own label when given one', () => {
    render(<StatusLamp status="online">Deck systems nominal</StatusLamp>);

    expect(screen.getByText('Deck systems nominal')).toBeVisible();
    expect(screen.queryByText('Online')).not.toBeInTheDocument();
  });
});
