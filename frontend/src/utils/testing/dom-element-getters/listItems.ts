import { within } from '@testing-library/react';

/** @description The text of each list item inside `container`, in order. */
export function getListItemTexts(container: HTMLElement): string[] {
  return within(container)
    .getAllByRole('listitem')
    .map(({ textContent }) => textContent ?? '');
}
