import { describe, expect, it } from 'vitest';

import { formatEpisodes, formatMeasurement, formatQuantity } from './format';

describe('format', () => {
  describe('formatMeasurement', () => {
    it.each([
      ['gross_weight_kg', 43400, '43,400 kg'],
      ['generator_output_kw', 1380, '1,380 kW'],
      ['max_acceleration_g', 0.93, '0.93 G'],
      ['max_speed_kmh', 165, '165 km/h'],
      ['turn_time_s', 1.5, '1.5 s'],
      ['head_height_m', 18, '18 m'],
    ] as const)('formats %s %d as %s', (field, value, formatted) => {
      expect(formatMeasurement({ field, value })).toBe(formatted);
    });

    it('gives null for a missing value', () => {
      expect(formatMeasurement({ field: 'sensor_range_m', value: null })).toBeNull();
    });
  });

  describe('formatQuantity', () => {
    it.each([
      [2, 2, '2 ×'],
      [1, 2, '1–2 ×'],
      [2, null, '2+ ×'],
      [null, 3, 'up to 3 ×'],
      [null, null, null],
    ])('formats %o to %o as %o', (quantity_min, quantity_max, formatted) => {
      expect(formatQuantity({ quantity_max, quantity_min })).toBe(formatted);
    });
  });

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
});
