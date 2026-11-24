import { screen, waitFor, within } from '@testing-library/react';
import { Response as MirageResponse, type Server } from 'miragejs';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import {
  mockMobileSuitDetails,
  mockRx7802Gundam,
  mockRx782Gundam,
  mockRx782GundamBaseSheet,
} from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitResponse } from '@/api';
import { safeFetch } from '@/utils';
import {
  getListItemTexts,
  getSpecPlateValue,
  renderWithProviders,
} from '@/utils/testing';

async function findDossier(name: string | RegExp = 'Gundam') {
  return screen.findByRole('region', { name });
}

describe('MobileSuitDetails', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('opens the dossier with the model number, names and class', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78-2-gundam'] });

    const dossier = await findDossier();
    expect(
      within(dossier).getByRole('heading', { level: 2, name: 'Gundam' }),
    ).toBeVisible();
    expect(within(dossier).getByText('RX-78-2', { selector: 'p' })).toBeVisible();
    expect(within(dossier).getByText('ガンダム')).toHaveAttribute('lang', 'ja');
    expect(within(dossier).getByText('Mobile Suit · Universal Century')).toBeVisible();
  });

  it('shows the first sheet and the credits in the infobox', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78-2-gundam'] });

    const infobox = await screen.findByRole('complementary', { name: 'Unit data' });
    expect(
      within(infobox).getByRole('figure', { name: 'No visual on file for Gundam' }),
    ).toBeVisible();
    expect(within(infobox).getByText('Base spec')).toBeVisible();

    const summary = within(infobox).getByLabelText('Spec summary');
    expect(
      getSpecPlateValue({ label: 'Head height', plate: summary }),
    ).toHaveTextContent('18 m');
    expect(
      getSpecPlateValue({ label: 'Gross weight', plate: summary }),
    ).toHaveTextContent('60,000 kg');
    expect(
      getSpecPlateValue({ label: 'Powerplant', plate: summary }),
    ).toHaveTextContent('Minovsky Ultracompact Fusion Reactor');
    expect(getSpecPlateValue({ label: 'Armor', plate: summary })).toHaveTextContent(
      'Luna Titanium Alloy',
    );
    expect(getSpecPlateValue({ label: 'Frame', plate: summary })).toHaveTextContent(
      'DATA PENDING',
    );

    const credits = within(infobox).getByLabelText('Credits');
    expect(
      within(getSpecPlateValue({ label: 'Designer', plate: credits })).getByRole(
        'link',
        {
          name: 'Kunio Okawara',
        },
      ),
    ).toHaveAttribute('href', '/mechanical-designers/kunio-okawara');
    expect(
      within(getSpecPlateValue({ label: 'Manufacturer', plate: credits })).getByRole(
        'link',
        {
          name: 'Earth Federation',
        },
      ),
    ).toHaveAttribute('href', '/organizations/earth-federation');
    expect(getSpecPlateValue({ label: 'Operator', plate: credits })).toHaveTextContent(
      'DATA PENDING',
    );
    expect(getSpecPlateValue({ label: 'Pilot', plate: credits })).toHaveTextContent(
      'Amuro Ray (Mobile Suit Gundam)',
    );
    expect(getSpecPlateValue({ label: 'Debut', plate: credits })).toHaveTextContent(
      'Mobile Suit Gundam · Episodes 1–43',
    );
  });

  it('shows the sheet that ?spec= names, with what it inherits', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({
      initialEntries: ['/mobile-suits/rx-78-2-gundam?spec=magnet-coating'],
    });

    const infobox = await screen.findByRole('complementary', { name: 'Unit data' });
    expect(within(infobox).getByText('Magnet Coating')).toBeVisible();
    expect(
      getSpecPlateValue({
        label: 'Gross weight',
        plate: within(infobox).getByLabelText('Spec summary'),
      }),
    ).toHaveTextContent('60,000 kgper base spec');
  });

  it('shows the first sheet for an unknown ?spec=', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78-2-gundam?spec=nope'] });

    const infobox = await screen.findByRole('complementary', { name: 'Unit data' });
    expect(within(infobox).getByText('Base spec')).toBeVisible();
  });

  it('lists the appearances, marking the debut', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78-2-gundam'] });

    const appearances = await screen.findByRole('region', { name: 'Appearances' });
    expect(getListItemTexts(appearances)).toEqual([
      'Mobile Suit Gundam[1]TV series · 1979 · Episodes 1–43Debut',
      'Mobile Suit Gundam I[1]Film · 1981',
    ]);
  });

  it('shows the pending registry rows and sections', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78-2-gundam'] });

    const registry = await screen.findByLabelText('Registry');
    expect(
      getSpecPlateValue({ label: 'Other names', plate: registry }),
    ).toHaveTextContent('DATA PENDING');
    for (const title of ['History', 'Gallery', 'Trivia']) {
      expect(screen.getByRole('region', { name: title })).toHaveTextContent(
        'DATA PENDING',
      );
    }
  });

  it('credits each distinct source once, and marks each fact with its number', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78-2-gundam'] });

    const sources = await screen.findByRole('region', { name: 'Sources' });
    const entries = within(sources).getAllByRole('listitem');
    // NOTE: the suit's own page, then each alternate version's page.
    expect(entries.map(({ id }) => id)).toEqual([
      'mobile-suit-source-1',
      'mobile-suit-source-2',
      'mobile-suit-source-3',
    ]);
    expect(
      within(entries[1]!).getByRole('link', { name: 'revision 707929' }),
    ).toBeVisible();

    const credits = screen.getByLabelText('Credits');
    expect(
      within(getSpecPlateValue({ label: 'Pilot', plate: credits })).getByRole('link', {
        name: 'Source 1',
      }),
    ).toHaveAttribute('href', '#mobile-suit-source-1');
  });

  it('swaps an old slug for the current one, keeping the search, without refetching', async () => {
    server = makeMirageServer({ environment: 'test' });
    const fetchSpy = vi.spyOn(safeFetch, 'call');
    const { router } = renderWithProviders({
      initialEntries: ['/mobile-suits', '/mobile-suits/rx-78-2?spec=magnet-coating'],
    });

    await findDossier();
    await waitFor(() =>
      expect(router.state.location.pathname).toBe('/mobile-suits/rx-78-2-gundam'),
    );
    expect(router.state.location.search).toBe('?spec=magnet-coating');
    expect(
      fetchSpy.mock.calls.filter(([{ name }]) => name === 'fetchMobileSuit'),
    ).toHaveLength(1);

    await router.navigate(-1);
    expect(router.state.location.pathname).toBe('/mobile-suits');
  });

  it('shows the empty cage for an unknown suit', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/turn-a-gundam'] });

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Cage empty' }),
    ).toBeVisible();
    expect(
      screen.getByText('NO UNIT ASSIGNED TO /mobile-suits/turn-a-gundam'),
    ).toBeVisible();
  });

  it('shows the error when the request fails', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/mobile-suits/:mobile_suit_slug',
          () => new MirageResponse(503, {}, {}),
        );
      },
    });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78-2-gundam'] });

    const page = await findDossier('Mobile suit dossier');
    expect(await within(page).findByRole('alert')).toHaveTextContent(
      'The mobile suit request failed.',
    );
  });

  it('shows a loading lamp until the suit arrives', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/mobile-suits/:mobile_suit_slug',
          (): MobileSuitResponse => ({
            data: mockMobileSuitDetails[mockRx782Gundam.slug]!,
          }),
          { timing: 50 },
        );
      },
    });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78-2-gundam'] });

    const page = await findDossier('Mobile suit dossier');
    expect(within(page).getByRole('status')).toHaveTextContent('Opening the dossier');
    expect(await findDossier()).toBeVisible();
  });

  it('shows pending values for a suit with few facts', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78f00-gundam'] });

    const dossier = await findDossier();
    expect(within(dossier).getByText('Mobile Suit', { selector: 'p' })).toBeVisible();
    const credits = within(dossier).getByLabelText('Credits');
    expect(getSpecPlateValue({ label: 'Pilot', plate: credits })).toHaveTextContent(
      'DATA PENDING',
    );
    expect(getSpecPlateValue({ label: 'Debut', plate: credits })).toHaveTextContent(
      'It Moves? Gundam, Follow Your Dreams!',
    );
  });

  it('lists several designers, and a pilot credit with no work', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: [`/mobile-suits/${mockRx7802Gundam.slug}`] });

    const credits = await screen.findByLabelText('Credits');
    expect(
      within(getSpecPlateValue({ label: 'Designers', plate: credits }))
        .getAllByRole('link')
        .filter((link) => !link.getAttribute('href')!.startsWith('#'))
        .map(({ textContent }) => textContent),
    ).toEqual(['Hajime Katoki', 'Kunio Okawara']);
    expect(getSpecPlateValue({ label: 'Pilot', plate: credits })).toHaveTextContent(
      /^Amuro Ray\[1\]$/,
    );
  });

  it('shows a suit with no sheet, model number, Japanese name or continuity', async () => {
    const rx782 = mockMobileSuitDetails[mockRx782Gundam.slug]!;
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/mobile-suits/:mobile_suit_slug', (): MobileSuitResponse => ({
          data: {
            ...rx782,
            continuity: null,
            model_number: null,
            name_ja: null,
            spec_sheets: [],
          },
        }));
      },
    });
    renderWithProviders({ initialEntries: [`/mobile-suits/${rx782.slug}`] });

    const dossier = await findDossier();
    expect(within(dossier).getByText('No model number')).toBeVisible();
    expect(within(dossier).getByText('Mobile Suit', { selector: 'p' })).toBeVisible();
    const summary = within(dossier).getByLabelText('Spec summary');
    expect(
      getSpecPlateValue({ label: 'Overall height', plate: summary }),
    ).toHaveTextContent('DATA PENDING');
    expect(
      getSpecPlateValue({ label: 'Powerplant', plate: summary }),
    ).toHaveTextContent('DATA PENDING');
  });

  it('prefers the overall height, and counts powerplants and frame materials', async () => {
    const rx782 = mockMobileSuitDetails[mockRx782Gundam.slug]!;
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/mobile-suits/:mobile_suit_slug', (): MobileSuitResponse => ({
          data: {
            ...rx782,
            spec_sheets: [
              {
                ...mockRx782GundamBaseSheet,
                materials: [
                  {
                    ...mockRx782GundamBaseSheet.materials[0]!,
                    material: { name: 'Gundarium', slug: 'gundarium' },
                    material_use: 'frame',
                  },
                ],
                overall_height_m: 19.5,
                powerplants: [
                  {
                    ...mockRx782GundamBaseSheet.powerplants[0]!,
                    quantity_max: 2,
                    quantity_min: 2,
                  },
                ],
              },
            ],
          },
        }));
      },
    });
    renderWithProviders({ initialEntries: [`/mobile-suits/${rx782.slug}`] });

    const summary = await screen.findByLabelText('Spec summary');
    expect(
      getSpecPlateValue({ label: 'Overall height', plate: summary }),
    ).toHaveTextContent('19.5 m');
    expect(
      getSpecPlateValue({ label: 'Powerplant', plate: summary }),
    ).toHaveTextContent('2 × Minovsky Ultracompact Fusion Reactor');
    expect(getSpecPlateValue({ label: 'Frame', plate: summary })).toHaveTextContent(
      'Gundarium',
    );
    expect(getSpecPlateValue({ label: 'Armor', plate: summary })).toHaveTextContent(
      'DATA PENDING',
    );
  });
});
