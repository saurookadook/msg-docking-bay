import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import {
  mockMobileSuitDetails,
  mockRx782Gundam,
  mockRx782GundamBaseSheet,
} from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitResponse } from '@/api';
import {
  getListItemTexts,
  getSpecPlateValue,
  renderWithProviders,
} from '@/utils/testing';

async function findSpecifications() {
  return screen.findByRole('region', { name: 'Specifications' });
}

const RX782_PATH = `/mobile-suits/${mockRx782Gundam.slug}`;

describe('SpecSheetTabs', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('shows a tab per sheet, the first selected, in a labelled panel', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: [RX782_PATH] });

    const specifications = await findSpecifications();
    const tabs = within(specifications).getAllByRole('tab');
    expect(tabs.map(({ textContent }) => textContent)).toEqual([
      'Base spec',
      'Magnet Coating',
    ]);
    expect(tabs[0]).toHaveAttribute('aria-selected', 'true');
    expect(tabs[0]).toHaveAttribute('tabindex', '0');
    expect(tabs[1]).toHaveAttribute('tabindex', '-1');

    const panel = within(specifications).getByRole('tabpanel', { name: 'Base spec' });
    expect(tabs[0]).toHaveAttribute('aria-controls', panel.id);
    const measurements = within(panel).getByLabelText('Measurements');
    expect(
      getSpecPlateValue({ label: 'Turn time', plate: measurements }),
    ).toHaveTextContent('1.5 s');
    expect(
      getSpecPlateValue({ label: 'Overall height', plate: measurements }),
    ).toHaveTextContent('DATA PENDING');
  });

  it('picks a sheet into ?spec= without a new history entry, and the infobox follows', async () => {
    server = makeMirageServer({ environment: 'test' });
    const { router } = renderWithProviders({
      initialEntries: ['/mobile-suits', RX782_PATH],
    });
    const user = userEvent.setup();

    await user.click(
      within(await findSpecifications()).getByRole('tab', { name: 'Magnet Coating' }),
    );

    expect(router.state.location.search).toBe('?spec=magnet-coating');
    const panel = screen.getByRole('tabpanel', { name: 'Magnet Coating' });
    const measurements = within(panel).getByLabelText('Measurements');
    expect(
      getSpecPlateValue({ label: 'Turn time', plate: measurements }),
    ).toHaveTextContent(/^1\.1 s$/);
    expect(
      getSpecPlateValue({ label: 'Gross weight', plate: measurements }),
    ).toHaveTextContent('60,000 kgper base spec');
    expect(
      within(panel).getByRole('heading', {
        level: 4,
        name: /^Armaments\s*· per base spec$/,
      }),
    ).toBeVisible();
    const infobox = screen.getByRole('complementary', { name: 'Unit data' });
    expect(within(infobox).getByText('Magnet Coating')).toBeVisible();
    const summary = within(infobox).getByLabelText('Spec summary');
    expect(getSpecPlateValue({ label: 'Armor', plate: summary })).toHaveTextContent(
      'Luna Titanium Alloyper base spec',
    );
    expect(getSpecPlateValue({ label: 'Frame', plate: summary })).toHaveTextContent(
      /^DATA PENDING$/,
    );

    await user.click(screen.getByRole('tab', { name: 'Base spec' }));
    expect(router.state.location.search).toBe('');

    await router.navigate(-1);
    expect(router.state.location.pathname).toBe('/mobile-suits');
  });

  it('moves between tabs with the arrow, Home and End keys', async () => {
    server = makeMirageServer({ environment: 'test' });
    const { router } = renderWithProviders({ initialEntries: [RX782_PATH] });
    const user = userEvent.setup();

    const [baseTab, magnetCoatingTab] = within(await findSpecifications()).getAllByRole(
      'tab',
    );
    await user.click(baseTab!);

    await user.keyboard('{ArrowRight}');
    expect(magnetCoatingTab).toHaveFocus();
    expect(router.state.location.search).toBe('?spec=magnet-coating');

    await user.keyboard('{ArrowRight}');
    expect(baseTab).toHaveFocus();
    expect(router.state.location.search).toBe('');

    await user.keyboard('{ArrowLeft}');
    expect(magnetCoatingTab).toHaveFocus();

    await user.keyboard('{Home}');
    expect(baseTab).toHaveFocus();

    await user.keyboard('{End}');
    expect(magnetCoatingTab).toHaveFocus();

    await user.keyboard('a');
    expect(magnetCoatingTab).toHaveAttribute('aria-selected', 'true');
  });

  it('groups armaments by mount and equipment by fit, with counts and notes', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: [RX782_PATH] });

    const panel = within(await findSpecifications()).getByRole('tabpanel');
    const listText = (name: string) =>
      getListItemTexts(within(panel).getByRole('list', { name }));

    expect(listText('Fixed')).toEqual(['2 ×60mm Vulcan Gun']);
    expect(listText('Handheld')).toEqual([
      '2 ×Beam Saber2 x Beam Javelin',
      'BOWA-XBR-M-79-07G Beam Rifle',
    ]);
    expect(listText('Optional')).toEqual([
      '1–2 ×BLASH-XHB-L-03/N-STD 380mm Hyper Bazookahandheld',
    ]);
    expect(listText('Standard')).toEqual([
      'Core Block System',
      'Magnet Coatingfield upgrade',
    ]);
    expect(listText('Powerplant')).toEqual(['Minovsky Ultracompact Fusion Reactor']);
    expect(listText('Armor')).toEqual(['Luna Titanium Alloy']);
  });

  it('shows one sheet without tabs, and a missing part kind as pending', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: ['/mobile-suits/ms-06f-zaku-ii'] });

    const specifications = await findSpecifications();
    expect(within(specifications).queryByRole('tablist')).not.toBeInTheDocument();
    expect(
      within(specifications).getByRole('heading', {
        level: 4,
        name: /^Base spec\s*Source 1$/,
      }),
    ).toBeVisible();
    expect(
      within(specifications).getByRole('region', { name: 'Powerplant' }),
    ).toHaveTextContent('DATA PENDING');
    expect(
      getListItemTexts(within(specifications).getByRole('list', { name: 'Optional' })),
    ).toEqual(['2 ×3-tube Missile Podfixed', 'MMP-80 90mm Machine Gunhandheld']);
  });

  it('shows pending specifications for a suit with no sheet', async () => {
    const rx782 = mockMobileSuitDetails[mockRx782Gundam.slug]!;
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/mobile-suits/:mobile_suit_slug', (): MobileSuitResponse => ({
          data: { ...rx782, spec_sheets: [] },
        }));
      },
    });
    renderWithProviders({ initialEntries: [RX782_PATH] });

    expect(await findSpecifications()).toHaveTextContent('SpecificationsDATA PENDING');
  });

  it('lists optional equipment apart from standard', async () => {
    /* START TEST SETUP */
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
                equipment: [
                  { ...mockRx782GundamBaseSheet.equipment[0]!, fit: 'optional' },
                ],
              },
            ],
          },
        }));
      },
    });
    renderWithProviders({ initialEntries: [RX782_PATH] });
    /* END TEST SETUP */

    const specifications = await findSpecifications();
    expect(
      within(specifications).queryByRole('list', { name: 'Standard' }),
    ).not.toBeInTheDocument();
    expect(
      within(
        within(specifications).getByRole('region', {
          name: 'Special equipment & features',
        }),
      ).getByRole('list', { name: 'Optional' }),
    ).toHaveTextContent('Core Block System');
  });
});
