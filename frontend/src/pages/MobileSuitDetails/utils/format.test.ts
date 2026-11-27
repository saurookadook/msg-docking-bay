import { describe, expect, it } from 'vitest';

import { formatMeasurement, formatMetres, formatQuantity } from './format';

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

  describe('formatMetres', () => {
    it('formats a length in metres', () => {
      expect(formatMetres(1.7)).toBe('1.7 m');
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
});
