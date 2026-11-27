import type { Nullable } from '@/types';

/** @description How a range of whole numbers reads: one value, a span, or one open end. */
export type RangeWording = {
  between: (args: { max: number; min: number }) => string;
  exactly: (value: number) => string;
  from: (min: number) => string;
  upTo: (max: number) => string;
};

/**
 * @description A range of whole numbers in `wording`: one value, a span, or one open end.
 * @returns `null` when neither end is known
 */
export function formatRange({
  max,
  min,
  wording,
}: {
  max: Nullable<number>;
  min: Nullable<number>;
  wording: RangeWording;
}): Nullable<string> {
  if (min != null && max != null) {
    return min === max ? wording.exactly(min) : wording.between({ max, min });
  }
  if (min != null) return wording.from(min);
  if (max != null) return wording.upTo(max);
  return null;
}

const EPISODE_WORDING: RangeWording = {
  between: ({ max, min }) => `Episodes ${min}–${max}`,
  exactly: (value) => `Episode ${value}`,
  from: (min) => `From episode ${min}`,
  upTo: (max) => `To episode ${max}`,
};

/**
 * @description An appearance's episodes: `Episodes 1–43`, `Episode 5`, `From episode 3`
 * or `To episode 9`.
 * @returns `null` when no episode was recorded
 */
export function formatEpisodes({
  first_episode,
  last_episode,
}: {
  first_episode: Nullable<number>;
  last_episode: Nullable<number>;
}): Nullable<string> {
  return formatRange({
    max: last_episode,
    min: first_episode,
    wording: EPISODE_WORDING,
  });
}
