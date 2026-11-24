import { screen, waitFor } from '@testing-library/react';
import type { Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockPrincipalityOfZeonRef, mockZeonic } from '@/__mocks__/peopleMocks';
import type { OrganizationsListResponse } from '@/api';
import { findRowHeaderTexts, renderWithProviders } from '@/utils/testing';

const TABLE_NAME = 'Organizations, by name';

describe('OrganizationList', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('lists the organizations, with no parent marked', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/organizations'] });

    expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toHaveLength(3);
    expect(screen.getAllByRole('cell', { name: '—' })).toHaveLength(3);
  });

  it('links a parent organization', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/organizations', (): OrganizationsListResponse => ({
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

    await waitFor(async () =>
      expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toHaveLength(2),
    );
  });
});
