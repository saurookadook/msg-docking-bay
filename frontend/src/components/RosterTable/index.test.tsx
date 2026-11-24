import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

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
});
