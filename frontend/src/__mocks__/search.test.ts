import { describe, expect, it } from 'vitest';

import { normalizeSearch, searchList } from './search';

describe('normalizeSearch', () => {
  it.each([
    ['RX 78-2', 'rx782'],
    ['rx-78-2', 'rx782'],
    ['∀ Gundam', 'gundam'],
    ['rx%_02', 'rx02'],
  ])('turns %s into %s', (q, needle) => {
    expect(normalizeSearch(q)).toBe(needle);
  });

  it.each([undefined, null, '', ' -- ', '%_', '大河原'])(
    'returns undefined for %o',
    (q) => {
      expect(normalizeSearch(q)).toBeUndefined();
    },
  );
});

describe('searchList', () => {
  const items = [
    { name: 'Act Zaku', slug: 'act-zaku' },
    { name: 'Gundam', slug: 'rx-78-2-gundam' },
    { name: 'Zaku II', slug: 'zaku-ii' },
  ];
  const columns = ({ name, slug }: (typeof items)[number]) => [slug, name];

  it('keeps matches, prefix matches first, the rest in their order', () => {
    expect(searchList({ columns, items, q: 'zaku' }).map(({ slug }) => slug)).toEqual([
      'zaku-ii',
      'act-zaku',
    ]);
  });

  it('matches any column', () => {
    expect(searchList({ columns, items, q: 'gundam' }).map(({ slug }) => slug)).toEqual(
      ['rx-78-2-gundam'],
    );
  });

  it('returns every item for a blank q', () => {
    expect(searchList({ columns, items, q: ' -- ' })).toBe(items);
  });
});
