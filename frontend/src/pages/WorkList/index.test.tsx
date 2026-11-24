import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Server } from 'miragejs';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockItMoves, mockMobileSuitGundam } from '@/__mocks__/workMocks';
import type { ContinuitiesListResponse, WorksListResponse } from '@/api';
import { safeFetch } from '@/utils';
import { renderWithProviders } from '@/utils/testing';

async function findRowTitles(): Promise<string[]> {
  const table = await screen.findByRole('table', {
    name: 'Works, first released first',
  });
  return within(table)
    .getAllByRole('rowheader')
    .map(({ textContent }) => textContent ?? '');
}

describe('WorkList', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('lists the works with their type, run and continuity', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/works'] });

    expect(await findRowTitles()).toHaveLength(5);
    const firstRow = screen.getAllByRole('row')[1]!;
    expect(
      within(firstRow)
        .getAllByRole('cell')
        .map(({ textContent }) => textContent),
    ).toEqual(['TV series', '1979-04-07 – 1980-01-26', 'Universal Century']);
    expect(screen.getByRole('cell', { name: '1981-03-04' })).toBeInTheDocument();
  });

  it('narrows by work type', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/works'] });
    const user = userEvent.setup();

    await findRowTitles();
    await user.selectOptions(screen.getByRole('combobox', { name: 'Type' }), 'Film');

    await waitFor(async () => expect(await findRowTitles()).toHaveLength(1));
  });

  it('asks for the continuities once, even when there are none', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/continuities', (): ContinuitiesListResponse => ({ data: [] }));
      },
    });
    const fetchSpy = vi.spyOn(safeFetch, 'call');
    renderWithProviders({ initialEntries: ['/works'] });

    const continuityCallIndexes = () =>
      fetchSpy.mock.calls.flatMap(([, { requestPathname }], index) =>
        requestPathname === '/api/continuities' ? [index] : [],
      );
    await waitFor(() => expect(continuityCallIndexes()).toHaveLength(1));
    await fetchSpy.mock.results[continuityCallIndexes()[0]!]?.value;
    await findRowTitles();

    expect(continuityCallIndexes()).toHaveLength(1);
  });

  it('marks a work with no dates, and one released on a single day', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/works', (): WorksListResponse => ({
          data: [
            { ...mockItMoves, end_date: null, start_date: null },
            { ...mockMobileSuitGundam, end_date: '1979-04-07' },
          ],
          meta: { limit: 50, offset: 0, total: 2 },
        }));
      },
    });
    renderWithProviders({ initialEntries: ['/works'] });

    expect(await screen.findAllByRole('cell', { name: '—' })).toHaveLength(2);
    expect(screen.getByRole('cell', { name: '1979-04-07' })).toBeInTheDocument();
  });
});
