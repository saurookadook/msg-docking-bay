import type { WorkType } from '@/api';
import type { Nullable } from '@/types';

// NOTE: a fixed locale and UTC, so an ISO date reads the same everywhere (and in tests),
// and never shifts a day west of Greenwich.
const dateFormat = new Intl.DateTimeFormat('en', {
  dateStyle: 'medium',
  timeZone: 'UTC',
});

/** @description An ISO date (`1979-04-07`) as the infobox gives it: `Apr 7, 1979`. */
export function formatDate(isoDate: string): string {
  return dateFormat.format(new Date(`${isoDate}T00:00:00Z`));
}

/**
 * @description A work's run: `Apr 7, 1979 – Jan 26, 1980`, or one date when only the
 * start is known or both are the same day.
 * @returns `null` when the start is unknown ("DATA PENDING")
 */
export function formatWorkDates({
  end_date,
  start_date,
}: {
  end_date: Nullable<string>;
  start_date: Nullable<string>;
}): Nullable<string> {
  if (start_date == null) return null;
  const start = formatDate(start_date);
  return end_date == null || end_date === start_date
    ? start
    : `${start} – ${formatDate(end_date)}`;
}

/** @description What a work's dates are called: when it aired, was published or released. */
export function workDatesLabel(workType: WorkType): string {
  switch (workType) {
    case 'tv_series':
    case 'ona':
      return 'Aired';
    case 'manga':
    case 'novel':
      return 'Published';
    default:
      return 'Released';
  }
}
