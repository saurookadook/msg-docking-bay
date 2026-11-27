import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Response as MirageResponse, type Server } from 'miragejs';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { paginate } from '@/__mocks__/endpoints';
import { makeMirageServer } from '@/__mocks__/mirageServer';
import { findWorkMobileSuitsMock } from '@/__mocks__/mobileSuitMocks';
import { findWorkMock } from '@/__mocks__/workMocks';
import type { WorkResponse } from '@/api';
import { safeFetch } from '@/utils';
import {
  getSpecPlateValue,
  renderWithProviders,
  requestPathsFor,
} from '@/utils/testing';

async function findLog(name: string = 'Mobile Suit Gundam') {
  return screen.findByRole('region', { name });
}

describe('WorkDetails', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
    vi.restoreAllMocks();
  });

  describe('when the work is loaded', () => {
    it('opens the log with the titles, type and continuity', async () => {
      server = makeMirageServer({ environment: 'test' });
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam'] });

      const log = await findLog();
      expect(
        within(log).getByRole('heading', { level: 2, name: 'Mobile Suit Gundam' }),
      ).toBeVisible();
      expect(within(log).getByText('機動戦士ガンダム')).toHaveAttribute('lang', 'ja');
      expect(
        within(log).getByText('TV series · Universal Century', { selector: 'p' }),
      ).toBeVisible();
    });

    it('shows the type, run, continuity and parent in the infobox', async () => {
      server = makeMirageServer({ environment: 'test' });
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam'] });

      const infobox = await screen.findByRole('complementary', {
        name: 'Operation data',
      });
      const plate = within(infobox).getByLabelText('Log');
      expect(getSpecPlateValue({ label: 'Type', plate })).toHaveTextContent(
        'TV series',
      );
      expect(getSpecPlateValue({ label: 'Aired', plate })).toHaveTextContent(
        'Apr 7, 1979 – Jan 26, 1980',
      );
      expect(getSpecPlateValue({ label: 'Continuity', plate })).toHaveTextContent(
        'Universal Century',
      );
      expect(getSpecPlateValue({ label: 'Part of', plate })).toHaveTextContent(
        'None on file',
      );
      for (const label of ['Studio', 'Episodes']) {
        expect(getSpecPlateValue({ label, plate })).toHaveTextContent('DATA PENDING');
      }
    });

    it('groups the related works, each cited', async () => {
      server = makeMirageServer({ environment: 'test' });
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam'] });

      const related = await screen.findByRole('region', { name: 'Related works' });
      const compiledIn = within(related).getByRole('list', { name: 'Compiled in' });
      expect(
        within(compiledIn).getByRole('link', { name: 'Mobile Suit Gundam I' }),
      ).toHaveAttribute('href', '/works/mobile-suit-gundam-i');
      expect(compiledIn).toHaveTextContent('Film · 1981');
      expect(
        within(compiledIn).getByRole('link', { name: 'Source 1' }),
      ).toHaveAttribute('href', '#work-source-1');
      const sources = screen.getByRole('region', { name: 'Sources' });
      expect(within(sources).getAllByRole('listitem')).toHaveLength(1);
    });

    it('lists the mobile weapons appearing, debuts first, with their episodes', async () => {
      server = makeMirageServer({ environment: 'test' });
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam'] });

      const section = await screen.findByRole('region', {
        name: 'Mobile weapons appearing',
      });
      const table = await within(section).findByRole('table', {
        name: 'Mobile weapons in this work, debuts first',
      });
      const [gundam, zaku] = within(table).getAllByRole('row').slice(1);
      expect(gundam).toHaveTextContent('RX-78-2');
      expect(within(gundam!).getByRole('rowheader')).toHaveTextContent('Gundam');
      expect(gundam).toHaveTextContent('Episodes 1–43');
      expect(within(gundam!).getByText('Debut')).toBeVisible();
      expect(within(zaku!).getByRole('rowheader')).toHaveTextContent('Zaku II');
      expect(within(section).getByText('2 on file')).toBeVisible();
    });
  });

  describe('when the work is a film in a parent work', () => {
    it('calls a film released, and links its parent work', async () => {
      /* START TEST SETUP */
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get('/works/:work_slug', (): WorkResponse => ({
            data: {
              ...findWorkMock('mobile-suit-gundam-i')!,
              parent_work: {
                slug: 'mobile-suit-gundam-trilogy',
                title: 'The Movie Trilogy',
              },
            },
          }));
        },
      });
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam-i'] });
      /* END TEST SETUP */

      const plate = await screen.findByLabelText('Log');
      expect(getSpecPlateValue({ label: 'Released', plate })).toHaveTextContent(
        'Mar 4, 1981',
      );
      expect(
        within(getSpecPlateValue({ label: 'Part of', plate })).getByRole('link', {
          name: 'The Movie Trilogy',
        }),
      ).toHaveAttribute('href', '/works/mobile-suit-gundam-trilogy');
    });
  });

  describe('when the work has no dates or continuity', () => {
    it('shows pending dates and continuity for a work with neither', async () => {
      /* START TEST SETUP */
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get('/works/:work_slug', (): WorkResponse => ({
            data: {
              ...findWorkMock('it-moves-gundam-follow-your-dreams')!,
              start_date: null,
            },
          }));
        },
      });
      renderWithProviders({
        initialEntries: ['/works/it-moves-gundam-follow-your-dreams'],
      });
      /* END TEST SETUP */

      const plate = await screen.findByLabelText('Log');
      expect(getSpecPlateValue({ label: 'Released', plate })).toHaveTextContent(
        'DATA PENDING',
      );
      expect(getSpecPlateValue({ label: 'Continuity', plate })).toHaveTextContent(
        'DATA PENDING',
      );
      expect(screen.getByText('Other', { selector: 'p' })).toBeVisible();
      expect(
        screen.queryByRole('region', { name: 'Related works' }),
      ).not.toBeInTheDocument();
      expect(screen.queryByRole('region', { name: 'Sources' })).not.toBeInTheDocument();
    });
  });

  describe('when a suit has no model number or episodes', () => {
    it('marks a suit with no model number or episodes with a dash', async () => {
      /* START TEST SETUP */
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get('/works/:work_slug/mobile-suits', (_schema, request) =>
            paginate(
              findWorkMobileSuitsMock('mobile-suit-gundam-i').map((suit) => ({
                ...suit,
                model_number: null,
              })),
              request,
            ),
          );
        },
      });
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam-i'] });
      /* END TEST SETUP */

      const section = await screen.findByRole('region', {
        name: 'Mobile weapons appearing',
      });
      const [first] = (await within(section).findAllByRole('row')).slice(1);
      expect(
        within(first!)
          .getAllByRole('cell')
          .map(({ textContent }) => textContent),
      ).toEqual(['—', 'Mobile Suit', '—', '—']);
    });
  });

  describe('when no suit appears', () => {
    it('says so when no suit appears', async () => {
      /* START TEST SETUP */
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get('/works/:work_slug/mobile-suits', (_schema, request) =>
            paginate([], request),
          );
        },
      });
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam'] });
      /* END TEST SETUP */

      const section = await screen.findByRole('region', {
        name: 'Mobile weapons appearing',
      });
      expect(await within(section).findByText('None on file')).toBeVisible();
    });
  });

  describe('when the slug is old', () => {
    it('swaps an old slug, keeping the page, and fetches the suits once', async () => {
      server = makeMirageServer({ environment: 'test' });
      const fetchSpy = vi.spyOn(safeFetch, 'call');
      const { router } = renderWithProviders({
        initialEntries: ['/works', '/works/msg?limit=1&offset=1'],
      });

      const section = await screen.findByRole('region', {
        name: 'Mobile weapons appearing',
      });
      expect(await within(section).findByText('2–2 of 2')).toBeVisible();
      expect(router.state.location).toMatchObject({
        pathname: '/works/mobile-suit-gundam',
        search: '?limit=1&offset=1',
      });
      expect(requestPathsFor({ fetchSpy, name: 'fetchWorkMobileSuits' })).toEqual([
        '/api/works/mobile-suit-gundam/mobile-suits?limit=1&offset=1',
      ]);

      await router.navigate(-1);
      await waitFor(() => expect(router.state.location.pathname).toBe('/works'));
    });
  });

  describe('when the reader moves to another work', () => {
    it("never shows the last work's suits on a related work's page", async () => {
      /* START TEST SETUP */
      const user = userEvent.setup();
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get(
            '/works/:work_slug/mobile-suits',
            (_schema, request) =>
              paginate(
                findWorkMobileSuitsMock(request.params['work_slug'] ?? ''),
                request,
              ),
            { timing: 50 },
          );
        },
      });
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam'] });
      /* END TEST SETUP */

      const first = await screen.findByRole('region', {
        name: 'Mobile weapons appearing',
      });
      await within(first).findByText('Episodes 1–43');
      await user.click(screen.getByRole('link', { name: 'Mobile Suit Gundam I' }));

      await findLog('Mobile Suit Gundam I');
      const next = screen.getByRole('region', { name: 'Mobile weapons appearing' });
      expect(within(next).queryByRole('table')).not.toBeInTheDocument();
      expect(within(next).getByRole('status')).toHaveTextContent('Scanning the deck');
      expect(await within(next).findByText('2 on file')).toBeVisible();
      expect(within(next).queryByText('Episodes 1–43')).not.toBeInTheDocument();
    });

    it("drops the last work's suits when they land after leaving it", async () => {
      /* START TEST SETUP */
      const user = userEvent.setup();
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get(
            '/works/:work_slug/mobile-suits',
            (_schema, request) => {
              const workSlug = request.params['work_slug'] ?? '';
              return paginate(findWorkMobileSuitsMock(workSlug), request);
            },
            { timing: 100 },
          );
        },
      });
      const fetchSpy = vi.spyOn(safeFetch, 'call');
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam'] });
      /* END TEST SETUP */

      // NOTE: leave before the first work's suits arrive.
      await user.click(
        await screen.findByRole('link', { name: 'Mobile Suit Gundam I' }),
      );

      await findLog('Mobile Suit Gundam I');
      const section = screen.getByRole('region', { name: 'Mobile weapons appearing' });
      expect(await within(section).findByText('2 on file')).toBeVisible();
      expect(within(section).queryByText('Episodes 1–43')).not.toBeInTheDocument();
      expect(requestPathsFor({ fetchSpy, name: 'fetchWorkMobileSuits' })).toEqual([
        '/api/works/mobile-suit-gundam/mobile-suits',
        '/api/works/mobile-suit-gundam-i/mobile-suits',
      ]);
    });
  });

  describe('when the suit request fails', () => {
    it("shows the sub-list's error in its section", async () => {
      /* START TEST SETUP */
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get(
            '/works/:work_slug/mobile-suits',
            () => new MirageResponse(503, {}, { detail: 'Deck offline' }),
          );
        },
      });
      renderWithProviders({ initialEntries: ['/works/mobile-suit-gundam'] });
      /* END TEST SETUP */

      const section = await screen.findByRole('region', {
        name: 'Mobile weapons appearing',
      });
      expect(await within(section).findByRole('alert')).toHaveTextContent(
        'Deck offline',
      );
    });
  });

  describe('when the work is unknown', () => {
    it('shows the empty cage for an unknown work', async () => {
      server = makeMirageServer({ environment: 'test' });
      renderWithProviders({ initialEntries: ['/works/turn-a-gundam'] });

      expect(
        await screen.findByRole('heading', { level: 2, name: 'Cage empty' }),
      ).toBeVisible();
    });
  });
});
