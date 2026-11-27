import { describe, expect, it } from 'vitest';

import { joinParts, yearOf } from './joinParts';

describe('joinParts', () => {
  it('joins the present parts with a dot, leaving the missing ones out', () => {
    expect(joinParts(['TV series', null, '1979', undefined])).toBe('TV series · 1979');
  });

  it('gives an empty line when no part is present', () => {
    expect(joinParts([null, undefined])).toBe('');
  });
});

describe('yearOf', () => {
  it('reads the year of an ISO date', () => {
    expect(yearOf('1979-04-07')).toBe('1979');
  });

  it.each([null, undefined])('gives null for a %o date', (date) => {
    expect(yearOf(date)).toBeNull();
  });
});
