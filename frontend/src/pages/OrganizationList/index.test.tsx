import { screen, waitFor, within } from '@testing-library/react';
import type { Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockPrincipalityOfZeonRef, mockZeonic } from '@/__mocks__/peopleMocks';
import { renderWithProviders } from '@/utils/testing';

async function findRowNames(): Promise<string[]> {
  const table = await screen.findByRole('table', { name: 'Organizations, by name' });
  return within(table)
    .getAllByRole('rowheader')
    .map(({ textContent }) => textContent ?? '');
}

describe('OrganizationList', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('lists the organizations, with no parent marked', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/organizations'] });

    expect(await findRowNames()).toHaveLength(3);
    expect(screen.getAllByRole('cell', { name: '—' })).toHaveLength(3);
  });

  it('links a parent organization', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/organizations', () => ({
          data: [{ ...mockZeonic, parent_organization: mockPrincipalityOfZeonRef }],
          meta: { limit: 50, offset: 0, total: 1 },
        }));
      },
    });
    renderWithProviders({ initialEntries: ['/organizations'] });

    expect(
      await screen.findByRole('link', { name: mockPrincipalityOfZeonRef.name }),
    ).toHaveAttribute('href', `/organizations/${mockPrincipalityOfZeonRef.slug}`);
  });

  it('filters by work', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/organizations?work=mobile-suit-gundam'] });

    await waitFor(async () => expect(await findRowNames()).toHaveLength(2));
  });
});
