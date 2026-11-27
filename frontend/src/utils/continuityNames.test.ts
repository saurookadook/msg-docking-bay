import { describe, expect, it } from 'vitest';

import { continuityNames } from './continuityNames';

const universalCentury = { name: 'Universal Century' };
const cosmicEra = { name: 'Cosmic Era' };

describe('continuityNames', () => {
  it('names each continuity once, in the order of the works', () => {
    expect(
      continuityNames([
        { work: { continuity: universalCentury } },
        { work: { continuity: cosmicEra } },
        { work: { continuity: universalCentury } },
      ]),
    ).toBe('Universal Century · Cosmic Era');
  });

  it('gives null when no work has a continuity', () => {
    expect(continuityNames([{ work: { continuity: null } }])).toBeNull();
    expect(continuityNames([])).toBeNull();
  });
});
