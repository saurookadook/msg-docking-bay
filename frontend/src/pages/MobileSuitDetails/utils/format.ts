import type { SpecSheetField } from '@/api';
import type { Nullable } from '@/types';
import { formatRange, type RangeWording } from '@/utils';

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

const QUANTITY_WORDING: RangeWording = {
  between: ({ max, min }) => `${min}–${max} ×`,
  exactly: (value) => `${value} ×`,
  from: (min) => `${min}+ ×`,
  upTo: (max) => `up to ${max} ×`,
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
