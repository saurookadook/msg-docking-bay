import { useTable, type RowData } from '@tanstack/react-table';
import classNames from 'classnames';

import { ROSTER_FEATURES, type RosterColumns } from './rosterColumns';

import './styles.css';

export type RosterTableProps<Row extends RowData> = Omit<
  React.TableHTMLAttributes<HTMLTableElement>,
  'children'
> & {
  caption: string;
  columns: RosterColumns<Row>;
  /**
   * @description Each row's unique key. Defaults to the row's `slug`; give one for rows
   * that have none, or that list one entity twice (one row per credit).
   */
  getRowID?: (row: Row) => string;
  rows: readonly Row[];
};

/**
 * @description A row's `slug`, the default row key.
 * @note It throws for a row with no `slug`: such a roster must pass `getRowID`.
 */
function rowSlug(row: unknown): string {
  if (typeof row === 'object' && row != null && 'slug' in row) {
    const { slug } = row;
    if (typeof slug === 'string') return slug;
  }
  throw new TypeError('[RosterTable] : a row with no slug needs a getRowID');
}

/**
 * @description A catalog roster: one table row per entity, keyed by its slug (or
 * `getRowID`), in the order the API sent them.
 * @note On a phone each row stacks, and each cell shows its column's header as a label.
 * The explicit roles keep the table's semantics where the phone layout's flex display
 * would otherwise strip them (Safari).
 */
export function RosterTable<Row extends RowData>({
  caption,
  className,
  columns,
  getRowID = rowSlug,
  rows,
  ...props
}: RosterTableProps<Row>) {
  const table = useTable({
    columns,
    data: rows,
    features: ROSTER_FEATURES,
    getRowId: (row) => getRowID(row),
  });

  return (
    <table className={classNames('roster-table', className)} role="table" {...props}>
      <caption className="stencil-label">{caption}</caption>
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id} role="row">
            {headerGroup.headers.map((header) => (
              <th key={header.id} role="columnheader" scope="col">
                <table.FlexRender header={header} />
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => (
          <tr key={row.id} role="row">
            {row.getAllCells().map((cell) => {
              const { header } = cell.column.columnDef;
              const label = typeof header === 'string' ? header : undefined;
              const content = <table.FlexRender cell={cell} />;
              return cell.column.columnDef.meta?.isRowHeader === true ? (
                <th data-label={label} key={cell.id} role="rowheader" scope="row">
                  {content}
                </th>
              ) : (
                <td data-label={label} key={cell.id} role="cell">
                  {content}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
