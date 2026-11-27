import { describe, expect, it } from 'vitest';

import { continuityLabel } from './continuityLabel';

const mockUniversalCentury = { name: 'Universal Century' };
const mockCosmicEra = { name: 'Cosmic Era' };

describe('continuityLabel', () => {
  it('names each continuity once, in the order of the works', () => {
    expect(
      continuityLabel([
        { work: { continuity: mockUniversalCentury } },
        { work: { continuity: mockCosmicEra } },
        { work: { continuity: mockUniversalCentury } },
      ]),
    ).toBe('Universal Century · Cosmic Era');
  });

  it('gives null when no work has a continuity', () => {
    expect(continuityLabel([{ work: { continuity: null } }])).toBeNull();
    expect(continuityLabel([])).toBeNull();
  });
});
