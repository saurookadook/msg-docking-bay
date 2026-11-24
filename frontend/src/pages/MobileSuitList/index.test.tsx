import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Response as MirageResponse, type Server } from 'miragejs';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockZakuII } from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitsListResponse } from '@/api';
import { safeFetch } from '@/utils';
import { findRowHeaderTexts, renderWithProviders } from '@/utils/testing';

async function findRoster() {
  return screen.findByRole('region', { name: 'Mobile Suits' });
}

const TABLE_NAME = /Mobile suits in their cages/;

describe('MobileSuitList', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('lists every suit with its cage, model number, unit type and continuity', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits'] });

    const roster = await findRoster();
    await waitFor(() =>
      expect(within(roster).getByRole('status')).toHaveTextContent('4 on file'),
    );
    const rows = within(roster).getAllByRole('row').slice(1);
    expect(
      rows.map((row) =>
        within(row)
          .getAllByRole('cell')
          .map(({ textContent }) => textContent),
      ),
    ).toEqual([
      ['MS DECK 01 · CAGE 01', 'RX-78-2', 'Mobile Suit', 'Universal Century'],
      ['MS DECK 01 · CAGE 02', 'RX-78-02', 'Mobile Suit', 'Universal Century'],
      ['MS DECK 01 · CAGE 03', 'RX-78F00', 'Mobile Suit', '—'],
      ['MS DECK 01 · CAGE 04', 'MS-06F', 'Mobile Suit', 'Universal Century'],
    ]);
    expect(within(rows[3]!).getByRole('link', { name: 'Zaku II' })).toHaveAttribute(
      'href',
      '/mobile-suits/ms-06f-zaku-ii',
    );
  });

  it('narrows the roster by continuity', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits'] });
    const user = userEvent.setup();

    await findRowHeaderTexts({ tableName: TABLE_NAME });
    await user.selectOptions(
      await screen.findByRole('combobox', { name: 'Continuity' }),
      await screen.findByRole('option', { name: 'Universal Century' }),
    );

    await waitFor(async () =>
      expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toHaveLength(3),
    );
  });

  it('searches as the user types', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits'] });
    const user = userEvent.setup();

    await user.type(
      await screen.findByRole('searchbox', { name: 'Search mobile suits' }),
      'zaku',
    );

    await waitFor(async () =>
      expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toEqual(['Zaku II']),
    );
  });

  it("titles an old work slug's chip and filters by the current slug", async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits?work=msg'] });

    expect(
      await screen.findByRole('button', {
        name: 'Remove the work filter: Mobile Suit Gundam',
      }),
    ).toBeInTheDocument();
    await waitFor(async () =>
      expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toEqual([
        'Gundam',
        'Zaku II',
      ]),
    );
  });

  it('keeps its page when it swaps an old work slug', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({
      initialEntries: ['/mobile-suits?work=msg&limit=1&offset=1'],
    });

    await waitFor(async () =>
      expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toEqual(['Zaku II']),
    );
  });

  it('shows an unknown work, and the empty roster with a way out', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({
      initialEntries: ['/mobile-suits?work=turn-a-gundam&limit=2'],
    });
    const user = userEvent.setup();

    await waitFor(() =>
      expect(screen.getByRole('list', { name: 'Active filters' })).toHaveTextContent(
        'Unknown work (turn-a-gundam)',
      ),
    );
    await user.click(await screen.findByRole('link', { name: 'Clear filters' }));

    expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toEqual([
      'Gundam',
      'Gundam',
    ]);
    expect(
      screen.queryByRole('list', { name: 'Active filters' }),
    ).not.toBeInTheDocument();
  });

  it("shows the API's message for a bad filter", async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits?unit_type=tank'] });

    expect(await screen.findByRole('alert')).toHaveTextContent(
      "unit_type: Input should be 'suit'",
    );
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('pages through the roster, keeping its filters', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({
      initialEntries: ['/mobile-suits?continuity=universal-century&limit=2'],
    });
    const user = userEvent.setup();

    expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toEqual([
      'Gundam',
      'Gundam',
    ]);
    await user.click(screen.getByRole('link', { name: 'Next' }));

    await waitFor(async () =>
      expect(await findRowHeaderTexts({ tableName: TABLE_NAME })).toEqual(['Zaku II']),
    );
    expect(
      screen.getByRole('cell', { name: 'MS DECK 01 · CAGE 03' }),
    ).toBeInTheDocument();
  });

  it('marks a suit with no model number', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/mobile-suits', (): MobileSuitsListResponse => ({
          data: [{ ...mockZakuII, model_number: null }],
          meta: { limit: 50, offset: 0, total: 1 },
        }));
      },
    });
    renderWithProviders({ initialEntries: ['/mobile-suits'] });

    expect(await screen.findByRole('cell', { name: '—' })).toBeInTheDocument();
  });

  it('drops a response that lands after leaving the page', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/mobile-suits',
          (): MobileSuitsListResponse => ({
            data: [mockZakuII],
            meta: { limit: 50, offset: 0, total: 1 },
          }),
          { timing: 50 },
        );
      },
    });
    const fetchSpy = vi.spyOn(safeFetch, 'call');
    renderWithProviders({ initialEntries: ['/mobile-suits'] });
    const user = userEvent.setup();

    await user.click(await screen.findByRole('link', { name: 'Deck systems' }));
    expect(
      await screen.findByRole('heading', { name: 'Health Check' }),
    ).toBeInTheDocument();
    // NOTE: the suits request is still in flight; wait for it to settle after leaving.
    await fetchSpy.mock.results[0]?.value;

    expect(
      screen.queryByRole('region', { name: 'Mobile Suits' }),
    ).not.toBeInTheDocument();
  });

  it('shows a failed request as an error', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/mobile-suits',
          () => new MirageResponse(503, {}, { detail: 'Deck offline' }),
        );
      },
    });
    renderWithProviders({ initialEntries: ['/mobile-suits'] });

    expect(await screen.findByRole('alert')).toHaveTextContent('Deck offline');
  });
});
