import { render, screen, waitFor, within } from '@testing-library/react';
import { Response as MirageResponse, type Server } from 'miragejs';
import { createMemoryRouter, RouterProvider } from 'react-router';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import {
  mockMobileSuitDetails,
  mockRx7802Gundam,
  mockRx782Gundam,
} from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitResponse } from '@/api';
import { routerConfig } from '@/app/router';
import { AppStoreProvider } from '@/store';
import { safeFetch } from '@/utils';
import { renderWithProviders } from '@/utils/testing';

async function findDossier(name: string | RegExp = 'Gundam') {
  return screen.findByRole('region', { name });
}

function plateValue(plate: HTMLElement, label: string) {
  const term = within(plate).getByText(label, { selector: 'dt' });
  return term.nextElementSibling as HTMLElement;
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
    expect(plateValue(summary, 'Head height')).toHaveTextContent('18 m');
    expect(plateValue(summary, 'Gross weight')).toHaveTextContent('60,000 kg');
    expect(plateValue(summary, 'Powerplant')).toHaveTextContent(
      'Minovsky Ultracompact Fusion Reactor',
    );
    expect(plateValue(summary, 'Armor')).toHaveTextContent('Luna Titanium Alloy');
    expect(plateValue(summary, 'Frame')).toHaveTextContent('DATA PENDING');

    const credits = within(infobox).getByLabelText('Credits');
    expect(
      within(plateValue(credits, 'Designer')).getByRole('link', {
        name: 'Kunio Okawara',
      }),
    ).toHaveAttribute('href', '/mechanical-designers/kunio-okawara');
    expect(
      within(plateValue(credits, 'Manufacturer')).getByRole('link', {
        name: 'Earth Federation',
      }),
    ).toHaveAttribute('href', '/organizations/earth-federation');
    expect(plateValue(credits, 'Operator')).toHaveTextContent('DATA PENDING');
    expect(plateValue(credits, 'Pilot')).toHaveTextContent(
      'Amuro Ray (Mobile Suit Gundam)',
    );
    expect(plateValue(credits, 'Debut')).toHaveTextContent(
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
      plateValue(within(infobox).getByLabelText('Spec summary'), 'Gross weight'),
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
    const items = within(appearances).getAllByRole('listitem');
    expect(items.map(({ textContent }) => textContent)).toEqual([
      'Mobile Suit Gundam[1]TV series · 1979 · Episodes 1–43Debut',
      'Mobile Suit Gundam I[1]Film · 1981',
    ]);
  });

  it('shows the pending registry rows and sections', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/rx-78-2-gundam'] });

    const registry = await screen.findByLabelText('Registry');
    expect(plateValue(registry, 'Other names')).toHaveTextContent('DATA PENDING');
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
      within(plateValue(credits, 'Pilot')).getByRole('link', { name: 'Source 1' }),
    ).toHaveAttribute('href', '#mobile-suit-source-1');
  });

  it('swaps an old slug for the current one, keeping the search, without refetching', async () => {
    server = makeMirageServer({ environment: 'test' });
    const fetchSpy = vi.spyOn(safeFetch, 'call');
    const router = createMemoryRouter(routerConfig, {
      initialEntries: ['/mobile-suits', '/mobile-suits/rx-78-2?spec=magnet-coating'],
    });
    render(
      <AppStoreProvider>
        <RouterProvider router={router} />
      </AppStoreProvider>,
    );

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
    expect(plateValue(credits, 'Pilot')).toHaveTextContent('DATA PENDING');
    expect(plateValue(credits, 'Debut')).toHaveTextContent(
      'It Moves? Gundam, Follow Your Dreams!',
    );
  });

  it('lists several designers, and a pilot credit with no work', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: [`/mobile-suits/${mockRx7802Gundam.slug}`] });

    const credits = await screen.findByLabelText('Credits');
    expect(
      within(plateValue(credits, 'Designers'))
        .getAllByRole('link')
        .filter((link) => !link.getAttribute('href')!.startsWith('#'))
        .map(({ textContent }) => textContent),
    ).toEqual(['Hajime Katoki', 'Kunio Okawara']);
    expect(plateValue(credits, 'Pilot')).toHaveTextContent(/^Amuro Ray\[1\]$/);
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
    expect(plateValue(summary, 'Overall height')).toHaveTextContent('DATA PENDING');
    expect(plateValue(summary, 'Powerplant')).toHaveTextContent('DATA PENDING');
  });

  it('prefers the overall height, and counts powerplants and frame materials', async () => {
    const rx782 = mockMobileSuitDetails[mockRx782Gundam.slug]!;
    const [baseSheet] = rx782.spec_sheets;
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/mobile-suits/:mobile_suit_slug', (): MobileSuitResponse => ({
          data: {
            ...rx782,
            spec_sheets: [
              {
                ...baseSheet!,
                materials: [
                  {
                    ...baseSheet!.materials[0]!,
                    material: { name: 'Gundarium', slug: 'gundarium' },
                    material_use: 'frame',
                  },
                ],
                overall_height_m: 19.5,
                powerplants: [
                  { ...baseSheet!.powerplants[0]!, quantity_max: 2, quantity_min: 2 },
                ],
              },
            ],
          },
        }));
      },
    });
    renderWithProviders({ initialEntries: [`/mobile-suits/${rx782.slug}`] });

    const summary = await screen.findByLabelText('Spec summary');
    expect(plateValue(summary, 'Overall height')).toHaveTextContent('19.5 m');
    expect(plateValue(summary, 'Powerplant')).toHaveTextContent(
      '2 × Minovsky Ultracompact Fusion Reactor',
    );
    expect(plateValue(summary, 'Frame')).toHaveTextContent('Gundarium');
    expect(plateValue(summary, 'Armor')).toHaveTextContent('DATA PENDING');
  });
});
