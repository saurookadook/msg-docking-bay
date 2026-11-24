import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { findRowHeaderTexts, renderWithProviders } from '@/utils/testing';

const TABLE_NAME = 'Mechanical designers, by name';

describe('DesignerList', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('lists the designers, and searches them with no other filter', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mechanical-designers'] });
    const user = userEvent.setup();

    expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toEqual([
      'Hajime Katoki',
      'Kunio Okawara',
      'Masaki Kawahara',
    ]);
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument();

    await user.type(
      screen.getByRole('searchbox', { name: 'Search designers' }),
      'okawara',
    );
    await waitFor(async () =>
      expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toEqual([
        'Kunio Okawara',
      ]),
    );
    expect(screen.getByRole('link', { name: 'Kunio Okawara' })).toHaveAttribute(
      'href',
      '/mechanical-designers/kunio-okawara',
    );
  });
});
