import { screen, waitFor, within } from '@testing-library/react';
import { Response as MirageResponse, type Server } from 'miragejs';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { findCharacterMock } from '@/__mocks__/characterMocks';
import { makeMirageServer } from '@/__mocks__/mirageServer';
import type { CharacterResponse } from '@/api';
import { safeFetch } from '@/utils';
import {
  getListItemTexts,
  getSpecPlateValue,
  renderWithProviders,
} from '@/utils/testing';

async function findPersonnelFile(name: string | RegExp = 'Amuro Ray') {
  return screen.findByRole('region', { name });
}

describe('CharacterDetails', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('opens the personnel file with the names and continuity', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/characters/amuro-ray'] });

    const file = await findPersonnelFile();
    expect(
      within(file).getByRole('heading', { level: 2, name: 'Amuro Ray' }),
    ).toBeVisible();
    expect(within(file).getByText('アムロ・レイ')).toHaveAttribute('lang', 'ja');
    expect(
      within(file).getByText('Universal Century', { selector: 'p' }),
    ).toBeVisible();
  });

  it('shows the portrait slot and pending ID card rows', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/characters/amuro-ray'] });

    const infobox = await screen.findByRole('complementary', {
      name: 'Personnel data',
    });
    expect(
      within(infobox).getByRole('figure', { name: 'No visual on file for Amuro Ray' }),
    ).toBeVisible();
    const idCard = within(infobox).getByLabelText('ID card');
    for (const label of ['Affiliation', 'Rank', 'Gender', 'Age', 'Voice actors']) {
      expect(getSpecPlateValue({ label, plate: idCard })).toHaveTextContent(
        'DATA PENDING',
      );
    }
  });

  it('racks the qualified units with their model number and work', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/characters/amuro-ray'] });

    const units = await screen.findByRole('region', { name: 'Qualified units' });
    expect(getListItemTexts(units)).toEqual(['RX-78-2Gundam[1](Mobile Suit Gundam)']);
    expect(within(units).getByRole('link', { name: /Gundam/ })).toHaveAttribute(
      'href',
      '/mobile-suits/rx-78-2-gundam',
    );
  });

  it('says so when no unit is on file', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/characters/:character_slug', (): CharacterResponse => ({
          data: { ...findCharacterMock('amuro-ray')!, piloted_mobile_suits: [] },
        }));
      },
    });
    renderWithProviders({ initialEntries: ['/characters/amuro-ray'] });

    const units = await screen.findByRole('region', { name: 'Qualified units' });
    expect(units).toHaveTextContent('None on file');
  });

  it('lists the appearances, and the pending sections', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/characters/amuro-ray'] });

    const appearances = await screen.findByRole('region', { name: 'Appearances' });
    expect(
      within(appearances).getAllByRole('link', { name: /^Mobile Suit/ }),
    ).toHaveLength(2);
    expect(appearances).toHaveTextContent('TV series · 1979');
    for (const title of [
      'Personality',
      'Skills',
      'History',
      'Relationships',
      'Quotes',
    ]) {
      expect(screen.getByRole('region', { name: title })).toHaveTextContent(
        'DATA PENDING',
      );
    }
  });

  it('credits each distinct source once, and marks each fact with its number', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/characters/amuro-ray'] });

    const sources = await screen.findByRole('region', { name: 'Sources' });
    // NOTE: the suit's page credits the pilot; his own page lists both works.
    expect(
      within(sources)
        .getAllByRole('listitem')
        .map(({ id }) => id),
    ).toEqual(['character-source-1', 'character-source-2']);
    const appearances = screen.getByRole('region', { name: 'Appearances' });
    expect(
      within(appearances)
        .getAllByRole('link', { name: 'Source 2' })
        .map((link) => link.getAttribute('href')),
    ).toEqual(['#character-source-2', '#character-source-2']);
  });

  it('swaps an old slug for the current one without refetching', async () => {
    server = makeMirageServer({ environment: 'test' });
    const fetchSpy = vi.spyOn(safeFetch, 'call');
    const { router } = renderWithProviders({
      initialEntries: ['/characters', '/characters/amuro'],
    });

    await findPersonnelFile();
    await waitFor(() =>
      expect(router.state.location.pathname).toBe('/characters/amuro-ray'),
    );
    expect(
      fetchSpy.mock.calls.filter(([{ name }]) => name === 'fetchCharacter'),
    ).toHaveLength(1);

    await router.navigate(-1);
    expect(router.state.location.pathname).toBe('/characters');
  });

  it('shows the empty cage for an unknown character', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/characters/char-aznable'] });

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Cage empty' }),
    ).toBeVisible();
  });

  it('shows the error when the request fails', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/characters/:character_slug',
          () => new MirageResponse(503, {}, {}),
        );
      },
    });
    renderWithProviders({ initialEntries: ['/characters/amuro-ray'] });

    const page = await findPersonnelFile('Personnel file');
    expect(await within(page).findByRole('alert')).toHaveTextContent(
      'The character request failed.',
    );
  });

  it('shows a character with no Japanese name, continuity or work tag', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/characters/:character_slug', (): CharacterResponse => {
          const character = findCharacterMock('amuro-ray-origin')!;
          return {
            data: {
              ...character,
              appearances: character.appearances.map((appearance) => ({
                ...appearance,
                work: { ...appearance.work, continuity: null },
              })),
              name_ja: null,
            },
          };
        });
      },
    });
    renderWithProviders({ initialEntries: ['/characters/amuro-ray-origin'] });

    const file = await findPersonnelFile();
    expect(within(file).getByText('Personnel', { selector: 'p' })).toBeVisible();
    expect(within(file).queryByText(/アムロ/)).not.toBeInTheDocument();
    const units = within(file).getByRole('region', { name: 'Qualified units' });
    expect(getListItemTexts(units)).toEqual(['RX-78-02Gundam[1]']);
  });
});
