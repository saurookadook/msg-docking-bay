import type { SpecSheetField } from '@/api';
import type { Nullable } from '@/types';

/** @description Each measurement's label and SI unit, in the order a spec plate lists them. */
export const MEASUREMENTS = {
  overall_height_m: { label: 'Overall height', unit: 'm' },
  head_height_m: { label: 'Head height', unit: 'm' },
  empty_weight_kg: { label: 'Empty weight', unit: 'kg' },
  gross_weight_kg: { label: 'Gross weight', unit: 'kg' },
  generator_output_kw: { label: 'Generator output', unit: 'kW' },
  total_thrust_kg: { label: 'Total thrust', unit: 'kg' },
  max_acceleration_g: { label: 'Max acceleration', unit: 'G' },
  max_speed_kmh: { label: 'Max speed', unit: 'km/h' },
  sensor_range_m: { label: 'Sensor range', unit: 'm' },
  turn_time_s: { label: 'Turn time', unit: 's' },
} as const satisfies Record<SpecSheetField, { label: string; unit: string }>;

// NOTE: a fixed locale, so the plates read the same everywhere (and in tests).
const numberFormat = new Intl.NumberFormat('en', { maximumFractionDigits: 2 });

/** @description A length in metres, such as `1.7 m`. */
export function formatMetres(value: number): string {
  return `${numberFormat.format(value)} m`;
}

/**
 * @description A measurement with its unit, such as `43,400 kg`.
 * @returns `null` when the sheet has no value ("DATA PENDING")
 */
export function formatMeasurement({
  field,
  value,
}: {
  field: SpecSheetField;
  value: Nullable<number>;
}): Nullable<string> {
  return value == null
    ? null
    : `${numberFormat.format(value)} ${MEASUREMENTS[field].unit}`;
}

/** @description How a range of whole numbers reads: one value, a span, or one open end. */
type RangeWording = {
  between: (args: { max: number; min: number }) => string;
  exactly: (value: number) => string;
  from: (min: number) => string;
  upTo: (max: number) => string;
};

/** @returns `null` when neither end is known */
function formatRange({
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

const QUANTITY_WORDING: RangeWording = {
  between: ({ max, min }) => `${min}–${max} ×`,
  exactly: (value) => `${value} ×`,
  from: (min) => `${min}+ ×`,
  upTo: (max) => `up to ${max} ×`,
};

const EPISODE_WORDING: RangeWording = {
  between: ({ max, min }) => `Episodes ${min}–${max}`,
  exactly: (value) => `Episode ${value}`,
  from: (min) => `From episode ${min}`,
  upTo: (max) => `To episode ${max}`,
};

/**
 * @description A part's count as the infobox gives it: `2 ×`, `1–2 ×`, `2+ ×` or
 * `up to 2 ×`.
 * @returns `null` when no count was given
 */
export function formatQuantity({
  quantity_max,
  quantity_min,
}: {
  quantity_max: Nullable<number>;
  quantity_min: Nullable<number>;
}): Nullable<string> {
  return formatRange({
    max: quantity_max,
    min: quantity_min,
    wording: QUANTITY_WORDING,
  });
}

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
