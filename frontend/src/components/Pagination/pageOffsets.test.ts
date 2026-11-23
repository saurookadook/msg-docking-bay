import { describe, expect, it } from 'vitest';

import { pageOffsets } from './pageOffsets';

describe('pageOffsets', () => {
  it('has only a next page on the first of several', () => {
    expect(pageOffsets({ limit: 50, offset: 0, total: 120 })).toEqual({
      firstRow: 1,
      lastRow: 50,
      nextOffset: 50,
      previousOffset: null,
    });
  });

  it('ends a partial last page at the total', () => {
    expect(pageOffsets({ limit: 50, offset: 100, total: 120 })).toEqual({
      firstRow: 101,
      lastRow: 120,
      nextOffset: null,
      previousOffset: 50,
    });
  });

  it('has neither page when every row fits', () => {
    expect(pageOffsets({ limit: 50, offset: 0, total: 3 })).toMatchObject({
      nextOffset: null,
      previousOffset: null,
    });
  });

  it('shows no rows on an empty list', () => {
    expect(pageOffsets({ limit: 50, offset: 0, total: 0 })).toEqual({
      firstRow: 0,
      lastRow: 0,
      nextOffset: null,
      previousOffset: null,
    });
  });

  it('steps back to the last real page from an offset past the end', () => {
    expect(pageOffsets({ limit: 50, offset: 400, total: 120 })).toEqual({
      firstRow: 0,
      lastRow: 0,
      nextOffset: null,
      previousOffset: 100,
    });
  });

  it.each([
    [{ limit: 50, offset: 120, total: 120 }, 100],
    [{ limit: 10, offset: 25, total: 25 }, 20],
    [{ limit: 10, offset: 29, total: 25 }, 20],
  ])(
    'steps back to the last real page from %o, just past the end',
    (meta, previousOffset) => {
      expect(pageOffsets(meta)).toMatchObject({ firstRow: 0, previousOffset });
    },
  );

  it('steps back to the start from an offset that is not a page boundary', () => {
    expect(pageOffsets({ limit: 50, offset: 30, total: 120 })).toMatchObject({
      previousOffset: 0,
    });
  });
});
