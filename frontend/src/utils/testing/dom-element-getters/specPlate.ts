import { within } from '@testing-library/react';

/**
 * @description The value cell (`dd`) beside the label in a `SpecPlate`.
 * @throws when the label has no value cell after it
 */
export function getSpecPlateValue({
  label,
  plate,
}: {
  label: string;
  plate: HTMLElement;
}): HTMLElement {
  const value = within(plate).getByText(label, { selector: 'dt' }).nextElementSibling;
  if (!(value instanceof HTMLElement)) {
    throw new Error(`[getSpecPlateValue] : no value after the label '${label}'`);
  }
  return value;
}
