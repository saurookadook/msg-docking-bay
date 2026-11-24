import { screen, within } from '@testing-library/react';
import type { Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import { mockSources } from '@/__mocks__/catalogMocks';
import { makeMirageServer } from '@/__mocks__/mirageServer';
import {
  mockMobileSuitDetails,
  mockRx7802Gundam,
  mockRx782Gundam,
  mockZakuII,
} from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitResponse } from '@/api';
import { getListItemTexts, renderWithProviders } from '@/utils/testing';

async function findLineage() {
  return screen.findByRole('region', { name: 'Variants & lineage' });
}

/** @description The text of each node in the lineage group with this label. */
function nodeTexts({ group, lineage }: { group: string; lineage: HTMLElement }) {
  return getListItemTexts(within(lineage).getByRole('list', { name: group }));
}

describe('SuitLineage', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('shows the suit with its alternate versions beside it, each sourced', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: [`/mobile-suits/${mockRx782Gundam.slug}`] });

    const lineage = await findLineage();
    expect(
      within(lineage).getByText('Gundam', { selector: 'span' }).parentElement,
    ).toHaveAttribute('aria-current', 'page');
    expect(nodeTexts({ group: 'Alternate versions', lineage })).toEqual([
      'RX-78-02Gundam[2]',
      'RX-78F00Gundam[3]',
    ]);
    expect(
      within(lineage)
        .getAllByRole('link', { name: 'Gundam' })
        .map((link) => link.getAttribute('href')),
    ).toEqual(['/mobile-suits/rx-78-02-gundam', '/mobile-suits/rx-78f00-gundam']);
  });

  it('places ancestors above and descendants below', async () => {
    const zaku = mockMobileSuitDetails[mockZakuII.slug]!;
    const relation = {
      created_at: zaku.created_at,
      source: mockSources.ms06fZakuII,
    };
    /* START TEST SETUP */
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/mobile-suits/:mobile_suit_slug', (): MobileSuitResponse => ({
          data: {
            ...zaku,
            relations: [
              {
                ...relation,
                direction: 'outgoing',
                mobile_suit: mockRx782Gundam,
                relation_type: 'developed_from',
              },
              {
                ...relation,
                direction: 'incoming',
                mobile_suit: { ...mockRx7802Gundam, model_number: null },
                relation_type: 'upgrade_of',
              },
            ],
          },
        }));
      },
    });
    renderWithProviders({ initialEntries: [`/mobile-suits/${mockZakuII.slug}`] });
    /* END TEST SETUP */

    const lineage = await findLineage();
    expect(
      within(lineage)
        .getAllByRole('heading', { level: 4 })
        .map(({ textContent }) => textContent),
    ).toEqual(['Developed from', 'Upgraded into']);
    expect(nodeTexts({ group: 'Developed from', lineage })).toEqual([
      'RX-78-2Gundam[1]',
    ]);
    expect(nodeTexts({ group: 'Upgraded into', lineage })).toEqual(['Gundam[1]']);
  });

  it('is left out for a suit with no relations', async () => {
    server = makeMirageServer({ environment: 'test' });
    renderWithProviders({ initialEntries: [`/mobile-suits/${mockZakuII.slug}`] });

    await screen.findByRole('region', { name: 'Specifications' });
    expect(
      screen.queryByRole('region', { name: 'Variants & lineage' }),
    ).not.toBeInTheDocument();
  });
});
