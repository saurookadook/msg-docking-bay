import { screen, within } from '@testing-library/react';

/**
 * @description Waits for the table with this accessible name, then returns the text of
 * each row header, in order.
 */
export async function findRowHeaderTexts({
  tableName,
}: {
  tableName: string | RegExp;
}): Promise<string[]> {
  const table = await screen.findByRole('table', { name: tableName });
  return within(table)
    .getAllByRole('rowheader')
    .map(({ textContent }) => textContent ?? '');
}
