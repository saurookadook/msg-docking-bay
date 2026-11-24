import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { renderWithProviders } from '@/utils/testing';

async function findRowNames(): Promise<string[]> {
  const table = await screen.findByRole('table', {
    name: 'Mechanical designers, by name',
  });
  return within(table)
    .getAllByRole('rowheader')
    .map(({ textContent }) => textContent ?? '');
}

describe('DesignerList', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('lists the designers, and searches them with no other filter', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mechanical-designers'] });
    const user = userEvent.setup();

    expect(await findRowNames()).toEqual([
      'Hajime Katoki',
      'Kunio Okawara',
      'Masaki Kawahara',
    ]);
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument();

    await user.type(
      screen.getByRole('searchbox', { name: 'Search designers' }),
      'okawara',
    );
    await waitFor(async () => expect(await findRowNames()).toEqual(['Kunio Okawara']));
    expect(screen.getByRole('link', { name: 'Kunio Okawara' })).toHaveAttribute(
      'href',
      '/mechanical-designers/kunio-okawara',
    );
  });
});
