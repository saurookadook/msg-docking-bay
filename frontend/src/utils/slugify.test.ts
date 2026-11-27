import { describe, expect, it } from 'vitest';

import { slugify } from './slugify';

describe('slugify', () => {
  it('lowercases ASCII words and joins them with dashes', () => {
    expect(slugify('  Magnet Coating (Café) ')).toBe('magnet-coating-cafe');
  });
});
