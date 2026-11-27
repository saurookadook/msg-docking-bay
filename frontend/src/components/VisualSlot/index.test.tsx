import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { VisualSlot } from '.';

describe('VisualSlot', () => {
  it('names the subject that has no visual yet', () => {
    render(<VisualSlot subject="RX-78-2 Gundam" />);

    expect(screen.getByRole('figure')).toHaveAccessibleName(
      'No visual on file for RX-78-2 Gundam',
    );
  });

  it('keeps its name when shrunk to a thumbnail', () => {
    render(<VisualSlot shape="thumbnail" subject="RX-78-2 Gundam" />);

    expect(screen.getByRole('figure')).toHaveAccessibleName(
      'No visual on file for RX-78-2 Gundam',
    );
  });
});
