import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { StencilHeading } from '.';

describe('StencilHeading', () => {
  it('renders a heading at the given level with its props', () => {
    render(
      <StencilHeading id="roster-title" level={2}>
        Cage roster
      </StencilHeading>,
    );

    expect(
      screen.getByRole('heading', { level: 2, name: 'Cage roster' }),
    ).toHaveAttribute('id', 'roster-title');
  });

  it('shows the eyebrow outside the heading name', () => {
    render(
      <StencilHeading eyebrow="MS DECK 02" level={3}>
        Cage roster
      </StencilHeading>,
    );

    expect(screen.getByText('MS DECK 02')).toBeVisible();
    expect(
      screen.getByRole('heading', { level: 3, name: 'Cage roster' }),
    ).toBeVisible();
  });
});
