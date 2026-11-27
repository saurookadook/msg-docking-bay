import { render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { RosterTable } from '.';
import { rosterColumnHelper } from './rosterColumns';

type Unit = { name: string; slug: string; unitType: string };

const helper = rosterColumnHelper<Unit>();
const columns = helper.columns([
  helper.accessor('name', { header: 'Name', meta: { isRowHeader: true } }),
  helper.accessor('unitType', { header: 'Unit type' }),
]);

const mockUnits: Unit[] = [
  { name: 'Gundam', slug: 'rx-78-2-gundam', unitType: 'Mobile Suit' },
  { name: 'Zaku II', slug: 'ms-06f-zaku-ii', unitType: 'Mobile Suit' },
];

describe('RosterTable', () => {
  it('renders a captioned table, one row per entity in the given order', () => {
    render(<RosterTable caption="Cage roster" columns={columns} rows={mockUnits} />);

    const table = screen.getByRole('table', { name: 'Cage roster' });
    expect(
      within(table)
        .getAllByRole('columnheader')
        .map(({ textContent }) => textContent),
    ).toEqual(['Name', 'Unit type']);
    expect(
      within(table)
        .getAllByRole('rowheader')
        .map(({ textContent }) => textContent),
    ).toEqual(['Gundam', 'Zaku II']);
  });

  it('labels each cell with its header for the stacked phone layout', () => {
    render(<RosterTable caption="Cage roster" columns={columns} rows={mockUnits} />);

    expect(screen.getAllByRole('cell')[0]).toHaveAttribute('data-label', 'Unit type');
    expect(screen.getAllByRole('rowheader')[0]).toHaveAttribute('data-label', 'Name');
  });

  it('states its table roles, which the phone layout would otherwise strip', () => {
    const { container } = render(
      <RosterTable caption="Cage roster" columns={columns} rows={mockUnits} />,
    );

    expect(
      [...container.querySelectorAll('table, tr, th, td')].map((element) =>
        element.getAttribute('role'),
      ),
    ).toEqual([
      'table',
      'row',
      'columnheader',
      'columnheader',
      'row',
      'rowheader',
      'cell',
      'row',
      'rowheader',
      'cell',
    ]);
  });

  it('leaves a cell unlabelled when its header is not plain text', () => {
    const columnsWithNodeHeader = helper.columns([
      helper.accessor('name', {
        header: () => <span>Name</span>,
        meta: { isRowHeader: true },
      }),
    ]);
    render(
      <RosterTable
        caption="Cage roster"
        columns={columnsWithNodeHeader}
        rows={mockUnits}
      />,
    );

    expect(screen.getAllByRole('rowheader')[0]).not.toHaveAttribute('data-label');
  });

  it('keys rows with getRowID, so one entity can fill two rows', () => {
    type Credit = { name: string; source: string };
    const creditHelper = rosterColumnHelper<Credit>();
    const creditColumns = creditHelper.columns([
      creditHelper.accessor('name', { header: 'Name', meta: { isRowHeader: true } }),
      creditHelper.accessor('source', { header: 'Source' }),
    ]);
    render(
      <RosterTable
        caption="Designed units"
        columns={creditColumns}
        getRowID={({ name, source }) => `${name}-${source}`}
        rows={[
          { name: 'Gundam', source: 'Gundam Wiki' },
          { name: 'Gundam', source: 'Wikidata' },
        ]}
      />,
    );

    expect(screen.getAllByRole('cell').map(({ textContent }) => textContent)).toEqual([
      'Gundam Wiki',
      'Wikidata',
    ]);
  });

  it('needs getRowID for rows with no slug', () => {
    const creditHelper = rosterColumnHelper<{ name: string }>();
    const creditColumns = creditHelper.columns([
      creditHelper.accessor('name', { header: 'Name' }),
    ]);
    // NOTE: React logs the error it rethrows; keep the test output quiet.
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() =>
      render(
        <RosterTable
          caption="Credits"
          columns={creditColumns}
          rows={[{ name: 'Gundam' }]}
        />,
      ),
    ).toThrow("[rowSlug] : a row with no string 'slug' needs a getRowID");
    const slugHelper = rosterColumnHelper<{ slug: number }>();
    expect(() =>
      render(
        <RosterTable
          caption="Credits"
          columns={slugHelper.columns([
            slugHelper.accessor('slug', { header: 'Slug' }),
          ])}
          rows={[{ slug: 7 }]}
        />,
      ),
    ).toThrow("[rowSlug] : a row with no string 'slug' needs a getRowID");
    consoleError.mockRestore();
  });
});
