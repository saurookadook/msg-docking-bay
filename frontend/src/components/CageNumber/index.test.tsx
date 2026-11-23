import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { CageNumber } from '.';

describe('CageNumber', () => {
  it('stencils the deck and cage as two-digit numbers', () => {
    render(<CageNumber cage={7} deck={2} />);

    expect(screen.getByText('MS DECK 02 · CAGE 07')).toBeVisible();
  });

  it('keeps numbers wider than two digits whole', () => {
    render(<CageNumber cage={124} deck={1} />);

    expect(screen.getByText('MS DECK 01 · CAGE 124')).toBeVisible();
  });
});
