import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Response as MirageResponse, type Server } from 'miragejs';
import { afterEach, describe, expect, it, vi, type MockInstance } from 'vitest';

import { mockNow, mockSources } from '@/__mocks__/catalogMocks';
import { paginate } from '@/__mocks__/endpoints';
import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockRx782Gundam } from '@/__mocks__/mobileSuitMocks';
import { findOrganizationMock } from '@/__mocks__/organizationMocks';
import type { OrganizationMobileSuitEntity, OrganizationResponse } from '@/api';
import { safeFetch } from '@/utils';
import { getSpecPlateValue, renderWithProviders } from '@/utils/testing';

async function findRegistry(name: string | RegExp = 'Earth Federation') {
  return screen.findByRole('region', { name });
}

/** @description The organization sub-list requests made, as their request paths. */
function subListRequests(fetchSpy: MockInstance<typeof safeFetch.call>): string[] {
  return fetchSpy.mock.calls
    .filter(([{ name }]) => name === 'fetchOrganizationMobileSuits')
    .map(([, { requestPathname }]) => requestPathname);
}

/** @description Three manufactured suits, so a one-row page has a next page. */
const manufacturedSuits: OrganizationMobileSuitEntity[] = ['a', 'b', 'c'].map(
  (suffix) => ({
    links: [
      {
        created_at: mockNow,
        role: 'manufacturer',
        source: mockSources.rx782Gundam,
        work: null,
      },
    ],
    mobile_suit: {
      ...mockRx782Gundam,
      name: `Gundam ${suffix}`,
      slug: `gundam-${suffix}`,
    },
  }),
);

describe('OrganizationDetails', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
    vi.restoreAllMocks();
  });

  it('opens the registry with the name and continuity', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/organizations/earth-federation'] });

    const registry = await findRegistry();
    expect(
      within(registry).getByRole('heading', { level: 2, name: 'Earth Federation' }),
    ).toBeVisible();
    expect(
      within(registry).getByText('Universal Century', { selector: 'p' }),
    ).toBeVisible();
  });

  it('shows the insignia slot, the parent and the pending rows', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/organizations/earth-federation'] });

    const infobox = await screen.findByRole('complementary', { name: 'Faction data' });
    expect(
      within(infobox).getByRole('figure', {
        name: 'No visual on file for the Earth Federation insignia',
      }),
    ).toBeVisible();
    const plate = within(infobox).getByLabelText('Registry');
    expect(getSpecPlateValue({ label: 'Parent', plate })).toHaveTextContent(
      'None on file',
    );
    for (const label of ['Type', 'Headquarters', 'Leaders', 'Founded', 'Dissolved']) {
      expect(getSpecPlateValue({ label, plate })).toHaveTextContent('DATA PENDING');
    }
    expect(screen.queryByRole('region', { name: 'Org chart' })).not.toBeInTheDocument();
  });

  it('charts the parent above and the units below', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/organizations/:organization_slug', (): OrganizationResponse => ({
          data: {
            ...findOrganizationMock('earth-federation')!,
            child_organizations: [
              { name: 'Earth Federation Forces', slug: 'earth-federation-forces' },
              { name: 'Titans', slug: 'titans' },
            ],
            parent_organization: { name: 'Earth Sphere', slug: 'earth-sphere' },
          },
        }));
      },
    });
    renderWithProviders({ initialEntries: ['/organizations/earth-federation'] });

    const chart = await screen.findByRole('region', { name: 'Org chart' });
    expect(
      within(within(chart).getByRole('list', { name: 'Parent' })).getByRole('link'),
    ).toHaveAttribute('href', '/organizations/earth-sphere');
    expect(
      within(within(chart).getByRole('list', { name: 'Units' }))
        .getAllByRole('link')
        .map(({ textContent }) => textContent),
    ).toEqual(['Earth Federation Forces', 'Titans']);
    expect(within(chart).getByText('Earth Federation')).toHaveAttribute(
      'aria-current',
      'page',
    );

    const plate = screen.getByLabelText('Registry');
    expect(
      within(getSpecPlateValue({ label: 'Parent', plate })).getByRole('link', {
        name: 'Earth Sphere',
      }),
    ).toBeVisible();
  });

  it('lists the mobile weapons by role, with an empty role as none on file', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/organizations/earth-federation'] });

    const manufactured = await screen.findByRole('region', { name: 'Manufactured' });
    const table = await within(manufactured).findByRole('table', {
      name: 'Manufactured mobile weapons, by name',
    });
    expect(within(table).getByRole('rowheader')).toHaveTextContent('Gundam[2]');
    expect(within(table).getByText('All works')).toBeVisible();
    for (const title of ['Operated', 'Developed']) {
      const section = screen.getByRole('region', { name: title });
      expect(await within(section).findByText('None on file')).toBeVisible();
      expect(within(section).queryByRole('table')).not.toBeInTheDocument();
    }
  });

  it('numbers the appearances first, then the role sections', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/organizations/earth-federation'] });

    const manufactured = await screen.findByRole('region', { name: 'Manufactured' });
    await within(manufactured).findByRole('table');
    const sources = screen.getByRole('region', { name: 'Sources' });
    expect(
      within(sources)
        .getAllByRole('listitem')
        .map(({ id }) => id),
    ).toEqual(['organization-source-1', 'organization-source-2']);
    expect(
      within(manufactured).getByRole('link', { name: 'Source 2' }),
    ).toHaveAttribute('href', '#organization-source-2');
  });

  it('pages one role section without refetching the others', async () => {
    const user = userEvent.setup();
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/organizations/:organization_slug/mobile-suits',
          (_schema, request) =>
            paginate(
              request.queryParams['role'] === 'manufacturer' ? manufacturedSuits : [],
              request,
            ),
        );
      },
    });
    const fetchSpy = vi.spyOn(safeFetch, 'call');
    const { router } = renderWithProviders({
      initialEntries: ['/organizations/earth-federation?limit=1'],
    });

    const manufactured = await screen.findByRole('region', { name: 'Manufactured' });
    expect(await within(manufactured).findByText('1–1 of 3')).toBeVisible();
    await user.click(within(manufactured).getByRole('link', { name: 'Next' }));

    expect(await within(manufactured).findByText('2–2 of 3')).toBeVisible();
    expect(router.state.location.search).toBe('?limit=1&manufacturer_offset=1');
    expect(within(manufactured).getByRole('rowheader')).toHaveTextContent('Gundam b');
    expect(subListRequests(fetchSpy).toSorted()).toEqual([
      '/api/organizations/earth-federation/mobile-suits?limit=1&offset=1&role=manufacturer',
      '/api/organizations/earth-federation/mobile-suits?limit=1&role=developer',
      '/api/organizations/earth-federation/mobile-suits?limit=1&role=manufacturer',
      '/api/organizations/earth-federation/mobile-suits?limit=1&role=operator',
    ]);
  });

  it("shows a role section's error in that section", async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/organizations/:organization_slug/mobile-suits',
          (_schema, request) =>
            request.queryParams['role'] === 'operator'
              ? new MirageResponse(503, {}, { detail: 'Deck offline' })
              : paginate([], request),
        );
      },
    });
    renderWithProviders({ initialEntries: ['/organizations/earth-federation'] });

    const operated = await screen.findByRole('region', { name: 'Operated' });
    expect(await within(operated).findByRole('alert')).toHaveTextContent(
      'Deck offline',
    );
    const developed = screen.getByRole('region', { name: 'Developed' });
    expect(within(developed).queryByRole('alert')).not.toBeInTheDocument();
  });

  it('swaps an old slug, fetching the organization and each section once', async () => {
    server = makeMirageServer({ environment: 'test' });
    const fetchSpy = vi.spyOn(safeFetch, 'call');
    const { router } = renderWithProviders({
      initialEntries: [
        '/organizations',
        '/organizations/earth-federation-universal-century',
      ],
    });

    const manufactured = await screen.findByRole('region', { name: 'Manufactured' });
    await within(manufactured).findByRole('table');
    expect(router.state.location.pathname).toBe('/organizations/earth-federation');
    expect(
      fetchSpy.mock.calls.filter(([{ name }]) => name === 'fetchOrganization'),
    ).toHaveLength(1);
    expect(subListRequests(fetchSpy)).toHaveLength(3);
    expect(
      subListRequests(fetchSpy).every((path) => path.includes('/earth-federation/')),
    ).toBe(true);

    await router.navigate(-1);
    await waitFor(() => expect(router.state.location.pathname).toBe('/organizations'));
  });

  it('shows the empty cage for an unknown organization', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/organizations/ζ-zeon'] });

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Cage empty' }),
    ).toBeVisible();
  });

  it('shows a faction with no appearances', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/organizations/zeonic'] });

    const registry = await findRegistry('Zeonic');
    expect(within(registry).getByText('Faction', { selector: 'p' })).toBeVisible();
    expect(
      within(registry).queryByRole('region', { name: 'Appearances' }),
    ).not.toBeInTheDocument();
    const manufactured = within(registry).getByRole('region', { name: 'Manufactured' });
    expect(await within(manufactured).findByRole('rowheader')).toHaveTextContent(
      'Zaku II',
    );
  });
});
