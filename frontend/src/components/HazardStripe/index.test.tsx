import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { HazardStripe } from '.';

describe('HazardStripe', () => {
  it('is decoration hidden from assistive technology', () => {
    const { container } = render(<HazardStripe crawling thick />);

    expect(container.firstChild).toHaveAttribute('aria-hidden', 'true');
  });
});
