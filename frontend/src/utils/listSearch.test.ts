import { describe, expect, it } from 'vitest';

import { listSearch, withoutSearchParams, withSearchParam } from './listSearch';

describe('listSearch', () => {
  it('keeps only the allowed, non-blank keys, sorted', () => {
    expect(
      listSearch({
        keys: ['unit_type', 'q', 'offset', 'continuity'],
        searchParams: new URLSearchParams(
          'unit_type=suit&foo=1&q=%20&offset=50&continuity=',
        ),
      }),
    ).toBe('offset=50&unit_type=suit');
  });

  it('gives the same string whatever order the URL has', () => {
    const keys = ['q', 'work'];

    expect(
      listSearch({ keys, searchParams: new URLSearchParams('work=w&q=gundam') }),
    ).toBe(listSearch({ keys, searchParams: new URLSearchParams('q=gundam&work=w') }));
  });
});

describe('withSearchParam', () => {
  it('sets a value and drops the offset', () => {
    expect(
      withSearchParam({
        name: 'q',
        searchParams: new URLSearchParams('limit=2&offset=4'),
        value: ' zaku ',
      }).toString(),
    ).toBe('limit=2&q=zaku');
  });

  it.each(['', '   ', null])('removes the param for %o', (value) => {
    expect(
      withSearchParam({
        name: 'q',
        searchParams: new URLSearchParams('q=zaku'),
        value,
      }).toString(),
    ).toBe('');
  });
});

describe('withoutSearchParams', () => {
  it('removes every named param and the offset, keeping the rest', () => {
    expect(
      withoutSearchParams({
        names: ['q', 'work'],
        searchParams: new URLSearchParams('q=a&work=b&limit=2&offset=2'),
      }).toString(),
    ).toBe('limit=2');
  });
});
