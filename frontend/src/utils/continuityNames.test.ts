import { describe, expect, it } from 'vitest';

import { continuityNames } from './continuityNames';

const mockUniversalCentury = { name: 'Universal Century' };
const mockCosmicEra = { name: 'Cosmic Era' };

describe('continuityNames', () => {
  it('names each continuity once, in the order of the works', () => {
    expect(
      continuityNames([
        { work: { continuity: mockUniversalCentury } },
        { work: { continuity: mockCosmicEra } },
        { work: { continuity: mockUniversalCentury } },
      ]),
    ).toBe('Universal Century · Cosmic Era');
  });

  it('gives null when no work has a continuity', () => {
    expect(continuityNames([{ work: { continuity: null } }])).toBeNull();
    expect(continuityNames([])).toBeNull();
  });
});
