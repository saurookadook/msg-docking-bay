import type { RowData } from '@tanstack/react-table';
import classNames from 'classnames';

import {
  DeckPanel,
  Pagination,
  RosterTable,
  StatusLamp,
  type RosterColumns,
} from '@/components';
import type { ListState } from '@/store';

import './styles.css';

export type RosterBodyProps<Row extends RowData> = Omit<
  React.HTMLAttributes<HTMLDivElement>,
  'children'
> & {
  caption: string;
  columns: RosterColumns<Row>;
  /** @description What the empty panel says when the page has no rows. */
  emptyState: React.ReactNode;
  getRowID?: (row: Row) => string;
  list: ListState<Row>;
  /** @description The search param its pager writes, when the page has several. */
  offsetParam?: string;
};

/**
 * @description A paged list's body: its status, error, empty state, roster and page
 * links. `CatalogRoster` frames it for a list page; a detail page puts one under each
 * of its sub-list headings.
 * @note The status region keeps one short message, so a live search announces the
 * result count rather than every request.
 */
export function RosterBody<Row extends RowData>({
  caption,
  className,
  columns,
  emptyState,
  getRowID,
  list,
  offsetParam,
  ...props
}: RosterBodyProps<Row>) {
  const { errorMessage, items, meta, requestInProgress } = list;

  return (
    <div className={classNames('roster-body', className)} {...props}>
      <p className="roster-body-status" role="status">
        {requestInProgress ? (
          <StatusLamp status="busy">Scanning the deck</StatusLamp>
        ) : (
          meta != null && `${meta.total} on file`
        )}
      </p>
      {errorMessage != null && (
        <p className="roster-body-error" role="alert">
          {errorMessage}
        </p>
      )}
      {errorMessage == null && meta != null && items.length === 0 && (
        <DeckPanel className="roster-body-empty">{emptyState}</DeckPanel>
      )}
      {items.length > 0 && (
        <RosterTable
          caption={caption}
          className={classNames({ stale: requestInProgress })}
          columns={columns}
          getRowID={getRowID}
          rows={items}
        />
      )}
      {meta != null && <Pagination meta={meta} offsetParam={offsetParam} />}
    </div>
  );
}
