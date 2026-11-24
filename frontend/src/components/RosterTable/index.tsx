import { useTable } from '@tanstack/react-table';
import classNames from 'classnames';

import { ROSTER_FEATURES, type RosterColumns } from './rosterColumns';

import './styles.css';

export type RosterTableProps<Row extends { slug: string }> = Omit<
  React.TableHTMLAttributes<HTMLTableElement>,
  'children'
> & {
  caption: string;
  columns: RosterColumns<Row>;
  /** @description The column whose cell names the row (a `<th scope="row">`). */
  rowHeaderColumnID: string;
  rows: readonly Row[];
};

/**
 * @description A catalog roster: one table row per entity, keyed by its slug, in the
 * order the API sent them.
 * @note On a phone each row stacks, and each cell shows its column's header as a label.
 */
export function RosterTable<Row extends { slug: string }>({
  caption,
  className,
  columns,
  rowHeaderColumnID,
  rows,
  ...props
}: RosterTableProps<Row>) {
  const table = useTable({
    columns,
    data: rows,
    features: ROSTER_FEATURES,
    getRowId: ({ slug }) => slug,
  });

  return (
    <table className={classNames('roster-table', className)} {...props}>
      <caption className="stencil-label">{caption}</caption>
      <thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => (
              <th key={header.id} scope="col">
                <table.FlexRender header={header} />
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => (
          <tr key={row.id}>
            {row.getAllCells().map((cell) => {
              const { header } = cell.column.columnDef;
              const label = typeof header === 'string' ? header : undefined;
              const content = <table.FlexRender cell={cell} />;
              return cell.column.id === rowHeaderColumnID ? (
                <th data-label={label} key={cell.id} scope="row">
                  {content}
                </th>
              ) : (
                <td data-label={label} key={cell.id}>
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
