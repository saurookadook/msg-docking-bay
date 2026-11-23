import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Readout } from '.';

describe('Readout', () => {
  it('keeps the whole line in the document while it types on', () => {
    render(<Readout typesOn>MS DECK 01 · STANDING BY</Readout>);

    const readoutText = screen.getByText('MS DECK 01 · STANDING BY');
    expect(readoutText).toBeVisible();
    expect(readoutText.style.getPropertyValue('--readout-chars')).toBe('24');
  });

  it('passes props to the paragraph', () => {
    render(
      <Readout isAmber role="status">
        Crane in motion
      </Readout>,
    );

    expect(screen.getByRole('status')).toHaveTextContent('Crane in motion');
  });
});
