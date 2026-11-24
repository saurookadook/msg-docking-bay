// The filters the mock list routes apply, as the API's list routes do (`endpoints.ts`).
import type { Nullable } from '@/types';

/**
 * @description One filter on a list route: its query param, and whether a row matches
 * a value. `allowed` lists an enum's values, and any other value is FastAPI's 422; a
 * slug filter has none, and an unknown slug matches nothing.
 */
export type ListFilter<T> = {
  allowed?: readonly string[];
  isMatch: (item: T, value: string) => boolean;
  param: string;
};

/** @description FastAPI's message for a value outside an enum: `'a', 'b' or 'c'`. */
export function enumMessage(allowed: readonly string[]): string {
  const quoted = allowed.map((value) => `'${value}'`);
  return `Input should be ${quoted.slice(0, -1).join(', ')} or ${quoted.at(-1)}`;
}

/** @description Filters rows by their continuity's current slug. */
export function continuityFilter<
  T extends { continuity: Nullable<{ slug: string }> },
>(): ListFilter<T> {
  return {
    isMatch: ({ continuity }, slug) => continuity?.slug === slug,
    param: 'continuity',
  };
}

/**
 * @description Filters rows to those that appear in a work, by the work's current slug
 * only, as the API's `work` filter does: an old slug matches nothing.
 */
export function workFilter<T extends { slug: string }>(
  appearances: (item: T) => readonly { work: { slug: string } }[] | undefined,
): ListFilter<T> {
  return {
    isMatch: (item, slug) =>
      appearances(item)?.some(({ work }) => work.slug === slug) ?? false,
    param: 'work',
  };
}
