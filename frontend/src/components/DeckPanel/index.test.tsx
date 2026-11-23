import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { DeckPanel } from '.';

describe('DeckPanel', () => {
  it('renders its children and passes props to the panel', () => {
    render(
      <DeckPanel aria-label="Cage 07" role="region">
        <p>Standing by</p>
      </DeckPanel>,
    );

    expect(screen.getByRole('region', { name: 'Cage 07' })).toHaveTextContent(
      'Standing by',
    );
  });
});
