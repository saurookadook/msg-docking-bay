import { screen, waitFor, within } from '@testing-library/react';
import type { Server } from 'miragejs';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { mockNow, mockSources, mockWikidataSource } from '@/__mocks__/catalogMocks';
import { paginate } from '@/__mocks__/endpoints';
import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockRx782Gundam } from '@/__mocks__/mobileSuitMocks';
import type { DesignedMobileSuitEntity } from '@/api';
import { safeFetch } from '@/utils';
import {
  getSpecPlateValue,
  renderWithProviders,
  requestPathsFor,
} from '@/utils/testing';

/** @description One suit credited by two sources; the second copy is sparse. */
const mockTwoSourceCredits: DesignedMobileSuitEntity[] = [
  {
    created_at: mockNow,
    mobile_suit: mockRx782Gundam,
    source: mockSources.rx782Gundam,
  },
  {
    created_at: mockNow,
    mobile_suit: { ...mockRx782Gundam, continuity: null, model_number: null },
    source: mockWikidataSource,
  },
];

async function findCredits(name: string = 'Kunio Okawara') {
  return screen.findByRole('region', { name });
}

async function findDesignedTable() {
  const section = await screen.findByRole('region', { name: 'Designed units' });
  return within(section).findByRole('table', {
    name: 'Mobile weapons credited to this designer, by name',
  });
}

describe('DesignerDetails', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
    vi.restoreAllMocks();
  });

  it('opens the credits with the names, and pending profile rows', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mechanical-designers/kunio-okawara'] });

    const credits = await findCredits();
    expect(
      within(credits).getByRole('heading', { level: 2, name: 'Kunio Okawara' }),
    ).toBeVisible();
    expect(within(credits).getByText('大河原 邦男')).toHaveAttribute('lang', 'ja');
    expect(
      within(credits).getByText('Mechanical designer', { selector: 'p' }),
    ).toBeVisible();
    const infobox = within(credits).getByRole('complementary', {
      name: 'Designer data',
    });
    for (const label of ['Born', 'Studio']) {
      expect(
        getSpecPlateValue({ label, plate: within(infobox).getByLabelText('Profile') }),
      ).toHaveTextContent('DATA PENDING');
    }
  });

  it('lists the designed units, each with its credit numbered', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mechanical-designers/kunio-okawara'] });

    const table = await findDesignedTable();
    expect(
      within(table)
        .getAllByRole('rowheader')
        .map(({ textContent }) => textContent),
    ).toEqual(['Gundam[1]', 'Gundam[2]', 'Zaku II[3]']);
    expect(within(table).getAllByText('Universal Century')).toHaveLength(3);
    const sources = screen.getByRole('region', { name: 'Sources' });
    expect(
      within(sources)
        .getAllByRole('listitem')
        .map(({ id }) => id),
    ).toEqual(['designer-source-1', 'designer-source-2', 'designer-source-3']);
  });

  it("cites only the shown page's credits", async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({
      initialEntries: ['/mechanical-designers/kunio-okawara?limit=1&offset=2'],
    });

    const table = await findDesignedTable();
    expect(within(table).getByRole('rowheader')).toHaveTextContent('Zaku II[1]');
    const sources = screen.getByRole('region', { name: 'Sources' });
    // NOTE: the Zaku II page's revision, the only credit on this page.
    expect(
      within(within(sources).getByRole('listitem')).getByRole('link', {
        name: 'revision 706593',
      }),
    ).toBeVisible();
  });

  it('lists a suit credited by two sources on two rows', async () => {
    /* START TEST SETUP */
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/mechanical-designers/:mechanical_designer_slug/mobile-suits',
          (_schema, request) => paginate(mockTwoSourceCredits, request),
        );
      },
    });
    renderWithProviders({ initialEntries: ['/mechanical-designers/kunio-okawara'] });
    /* END TEST SETUP */

    const table = await findDesignedTable();
    expect(
      within(table)
        .getAllByRole('rowheader')
        .map(({ textContent }) => textContent),
    ).toEqual(['Gundam[1]', 'Gundam[2]']);
    const [, , second] = within(table).getAllByRole('row');
    expect(
      within(second!)
        .getAllByRole('cell')
        .map(({ textContent }) => textContent),
    ).toEqual(['—', 'Mobile Suit', '—']);
  });

  it('says so, and lists no sources, for a designer with no credits', async () => {
    /* START TEST SETUP */
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/mechanical-designers/:mechanical_designer_slug/mobile-suits',
          (_schema, request) => paginate([], request),
        );
      },
    });
    renderWithProviders({ initialEntries: ['/mechanical-designers/masaki-kawahara'] });
    /* END TEST SETUP */

    const credits = await findCredits('Masaki Kawahara');
    const section = within(credits).getByRole('region', { name: 'Designed units' });
    expect(await within(section).findByText('None on file')).toBeVisible();
    expect(
      within(credits).queryByRole('region', { name: 'Sources' }),
    ).not.toBeInTheDocument();
    expect(within(credits).queryByText(/[ぁ-んァ-ン一-龯]/)).not.toBeInTheDocument();
  });

  it('swaps an old slug, fetching the designer and the credits once', async () => {
    server = makeMirageServer({ environment: 'test' });
    const fetchSpy = vi.spyOn(safeFetch, 'call');
    const { router } = renderWithProviders({
      initialEntries: ['/mechanical-designers', '/mechanical-designers/katoki-hajime'],
    });

    await findCredits('Hajime Katoki');
    await findDesignedTable();
    expect(router.state.location.pathname).toBe('/mechanical-designers/hajime-katoki');
    expect(
      requestPathsFor({ fetchSpy, name: 'fetchMechanicalDesignerMobileSuits' }),
    ).toEqual(['/api/mechanical-designers/hajime-katoki/mobile-suits']);

    await router.navigate(-1);
    await waitFor(() =>
      expect(router.state.location.pathname).toBe('/mechanical-designers'),
    );
  });

  it('shows the empty cage for an unknown designer', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({
      initialEntries: ['/mechanical-designers/yoshikazu-yasuhiko'],
    });

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Cage empty' }),
    ).toBeVisible();
  });
});
