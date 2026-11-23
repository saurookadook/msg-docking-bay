import { describe, expect, it } from 'vitest';

import { entityPath } from './entityPath';

describe('entityPath', () => {
  it.each([
    ['character', 'amuro-ray', '/characters/amuro-ray'],
    ['mechanicalDesigner', 'kunio-okawara', '/mechanical-designers/kunio-okawara'],
    ['mobileSuit', 'rx-78-2-gundam', '/mobile-suits/rx-78-2-gundam'],
    ['organization', 'earth-federation', '/organizations/earth-federation'],
    ['work', 'mobile-suit-gundam', '/works/mobile-suit-gundam'],
  ] as const)('builds the %s page path', (kind, slug, path) => {
    expect(entityPath({ kind, slug })).toBe(path);
  });

  it("builds the kind's list path without a slug", () => {
    expect(entityPath({ kind: 'mobileSuit' })).toBe('/mobile-suits');
  });

  it('encodes a slug that needs it', () => {
    expect(entityPath({ kind: 'work', slug: 'a/b' })).toBe('/works/a%2Fb');
  });
});
