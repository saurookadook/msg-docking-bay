import type { Nullable } from '@/types';

/** @description The separator between the parts of a meta or class line. */
const PART_SEPARATOR = ' · ';

/**
 * @description Joins the parts that are present into one meta line:
 * `TV series · 1979 · Episodes 1–43`. A `null` or `undefined` part is left out.
 * @returns `''` when no part is present
 */
export function joinParts(parts: readonly (Nullable<string> | undefined)[]): string {
  return parts.filter((part) => part != null).join(PART_SEPARATOR);
}

/**
 * @description The year of an ISO date (`1979-04-07` → `1979`).
 * @returns `null` for a missing date
 */
export function yearOf(date: Nullable<string> | undefined): Nullable<string> {
  return date?.slice(0, 4) ?? null;
}
