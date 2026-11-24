import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockAmuroRay } from '@/__mocks__/peopleMocks';
import type { CharactersListResponse } from '@/api';
import { renderWithProviders } from '@/utils/testing';

async function findRowNames(): Promise<string[]> {
  const table = await screen.findByRole('table', { name: 'Personnel files, by name' });
  return within(table)
    .getAllByRole('rowheader')
    .map(({ textContent }) => textContent ?? '');
}

describe('CharacterList', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('lists the personnel with their Japanese names, linking each file', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/characters'] });

    expect(await findRowNames()).toHaveLength(2);
    expect(screen.getAllByRole('link', { name: mockAmuroRay.name })[0]).toHaveAttribute(
      'href',
      `/characters/${mockAmuroRay.slug}`,
    );
    expect(screen.getAllByRole('cell')[0]).toHaveAttribute(
      'data-label',
      'Japanese name',
    );
  });

  it('filters by work, shown as a chip', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({
      initialEntries: ['/characters?work=mobile-suit-gundam-the-origin'],
    });

    await waitFor(async () => expect(await findRowNames()).toHaveLength(1));
    expect(
      await screen.findByRole('button', {
        name: /^Remove the work filter: Mobile Suit Gundam: The Origin/,
      }),
    ).toBeInTheDocument();
  });

  it('marks a character with no Japanese name', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/characters', (): CharactersListResponse => ({
          data: [{ ...mockAmuroRay, name_ja: null }],
          meta: { limit: 50, offset: 0, total: 1 },
        }));
      },
    });
    renderWithProviders({ initialEntries: ['/characters'] });

    expect(await screen.findByRole('cell', { name: '—' })).toBeInTheDocument();
  });

  it('searches as the user types', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/characters'] });
    const user = userEvent.setup();

    await user.type(
      await screen.findByRole('searchbox', { name: 'Search personnel' }),
      'origin',
    );

    await waitFor(async () => expect(await findRowNames()).toHaveLength(1));
  });
});
