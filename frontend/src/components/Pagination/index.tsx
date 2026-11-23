import classNames from 'classnames';
import { Link, useSearchParams } from 'react-router';

import type { PageMeta } from '@/api';
import type { Nullable } from '@/types';

import { pageOffsets } from './pageOffsets';

import './styles.css';

export type PaginationProps = React.HTMLAttributes<HTMLElement> & {
  meta: PageMeta;
};

/**
 * @description Previous and next links for a paginated list. They change only the URL's
 * `offset`, keeping its other search params (filters, `q`).
 * @returns nothing when every row fits on the first page
 */
export function Pagination({ className, meta, ...props }: PaginationProps) {
  const [searchParams] = useSearchParams();
  const { firstRow, lastRow, nextOffset, previousOffset } = pageOffsets(meta);

  if (previousOffset == null && nextOffset == null) return null;

  function searchWithOffset(offset: number): string {
    const nextSearchParams = new URLSearchParams(searchParams);
    if (offset === 0) {
      nextSearchParams.delete('offset');
    } else {
      nextSearchParams.set('offset', String(offset));
    }
    const search = nextSearchParams.toString();
    return search === '' ? '' : `?${search}`;
  }

  function renderPageLink(label: string, offset: Nullable<number>) {
    if (offset == null) {
      return (
        <span className="pagination-link unavailable">
          {label}
          <span className="visually-hidden"> (unavailable)</span>
        </span>
      );
    }
    return (
      <Link className="pagination-link" to={{ search: searchWithOffset(offset) }}>
        {label}
      </Link>
    );
  }

  return (
    <nav
      aria-label="Pagination"
      className={classNames('pagination', className)}
      {...props}
    >
      {renderPageLink('Previous', previousOffset)}
      <p className="pagination-range">
        {firstRow === 0
          ? `None of ${meta.total}`
          : `${firstRow}–${lastRow} of ${meta.total}`}
      </p>
      {renderPageLink('Next', nextOffset)}
    </nav>
  );
}
