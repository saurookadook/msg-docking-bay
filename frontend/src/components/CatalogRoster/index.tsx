import classNames from 'classnames';
import { Link, useSearchParams } from 'react-router';

import { RosterBody, StencilHeading, type RosterColumns } from '@/components';
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
};

/**
 * @description A catalog list page's frame: its heading and filters, then the roster
 * with its status, error, empty state and page links (`RosterBody`).
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
  ...props
}: CatalogRosterProps<Row>) {
  const [searchParams] = useSearchParams();
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
      <RosterBody
        caption={caption}
        columns={columns}
        emptyState={
          <>
            <p>No entries match these filters.</p>
            <Link to={{ search: limit == null ? '' : `?limit=${limit}` }}>
              Clear filters
            </Link>
          </>
        }
        list={list}
      />
    </section>
  );
}
