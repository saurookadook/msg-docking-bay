import classNames from 'classnames';
import { Link, useSearchParams } from 'react-router';

import {
  DeckPanel,
  Pagination,
  RosterTable,
  StatusLamp,
  StencilHeading,
  type RosterColumns,
} from '@/components';
import type { ListState } from '@/store';

import './styles.css';

export type CatalogRosterProps<Row extends { slug: string }> = Omit<
  React.HTMLAttributes<HTMLElement>,
  'children'
> & {
  caption: string;
  columns: RosterColumns<Row>;
  eyebrow: string;
  /** @description The page's `FilterBar`. */
  filterBar: React.ReactNode;
  heading: string;
  id: string;
  list: ListState<Row>;
  rowHeaderColumnID: string;
};

/**
 * @description A catalog list page's frame: its heading and filters, then the roster
 * with its status, error, empty state and page links.
 * @note The status region keeps one short message, so a live search announces the
 * result count rather than every request.
 */
export function CatalogRoster<Row extends { slug: string }>({
  caption,
  className,
  columns,
  eyebrow,
  filterBar,
  heading,
  id,
  list,
  rowHeaderColumnID,
  ...props
}: CatalogRosterProps<Row>) {
  const [searchParams] = useSearchParams();
  const { errorMessage, items, meta, requestInProgress } = list;
  const headingID = `${id}-title`;
  const limit = searchParams.get('limit');

  return (
    <section
      aria-labelledby={headingID}
      className={classNames('catalog-roster', className)}
      id={id}
      {...props}
    >
      <StencilHeading eyebrow={eyebrow} id={headingID} level={2}>
        {heading}
      </StencilHeading>
      {filterBar}
      <p className="catalog-roster-status" role="status">
        {requestInProgress ? (
          <StatusLamp status="busy">Scanning the deck</StatusLamp>
        ) : (
          meta != null && `${meta.total} on file`
        )}
      </p>
      {errorMessage != null && (
        <p className="catalog-roster-error" role="alert">
          {errorMessage}
        </p>
      )}
      {errorMessage == null && meta != null && items.length === 0 && (
        <DeckPanel className="catalog-roster-empty">
          <p>No entries match these filters.</p>
          <Link to={{ search: limit == null ? '' : `?limit=${limit}` }}>
            Clear filters
          </Link>
        </DeckPanel>
      )}
      {items.length > 0 && (
        <RosterTable
          caption={caption}
          className={classNames({ stale: requestInProgress })}
          columns={columns}
          rowHeaderColumnID={rowHeaderColumnID}
          rows={items}
        />
      )}
      {meta != null && <Pagination meta={meta} />}
    </section>
  );
}
