import { describe, expect, it } from 'vitest';

import { formatDate, formatWorkDates, workDatesLabel } from './dates';

describe('dates', () => {
  it('formats an ISO date in UTC, so it never shifts a day', () => {
    expect(formatDate('1979-04-07')).toBe('Apr 7, 1979');
    expect(formatDate('1980-01-01')).toBe('Jan 1, 1980');
  });

  it.each([
    ['1979-04-07', '1980-01-26', 'Apr 7, 1979 – Jan 26, 1980'],
    ['1981-03-04', null, 'Mar 4, 1981'],
    ['1981-03-04', '1981-03-04', 'Mar 4, 1981'],
    [null, '1980-01-26', null],
    [null, null, null],
  ])('formats a run from %o to %o as %o', (start_date, end_date, formatted) => {
    expect(formatWorkDates({ end_date, start_date })).toBe(formatted);
  });

  it.each([
    ['tv_series', 'Aired'],
    ['ona', 'Aired'],
    ['manga', 'Published'],
    ['novel', 'Published'],
    ['film', 'Released'],
    ['ova', 'Released'],
    ['video_game', 'Released'],
    ['other', 'Released'],
  ] as const)('calls the dates of a %s %o', (workType, label) => {
    expect(workDatesLabel(workType)).toBe(label);
  });
});
