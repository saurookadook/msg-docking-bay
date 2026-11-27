import { describe, expect, it } from 'vitest';

import { formatEpisodes } from './formatRange';

describe('formatEpisodes', () => {
  it.each([
    [1, 43, 'Episodes 1–43'],
    [5, 5, 'Episode 5'],
    [3, null, 'From episode 3'],
    [null, 9, 'To episode 9'],
    [null, null, null],
  ])('formats %o to %o as %o', (first_episode, last_episode, formatted) => {
    expect(formatEpisodes({ first_episode, last_episode })).toBe(formatted);
  });
});
