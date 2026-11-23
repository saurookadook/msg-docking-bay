import type { PageMeta } from '@/api';
import type { Nullable } from '@/types';

export type PageOffsets = {
  /** @description The first shown row's 1-based number, or `0` on an empty page. */
  firstRow: number;
  /** @description The last shown row's 1-based number. */
  lastRow: number;
  previousOffset: Nullable<number>;
  nextOffset: Nullable<number>;
};

/**
 * @description Works out the rows a page shows and the offsets either side of it.
 * @note An `offset` past the end (a stale or hand-edited URL) shows no rows, and its
 * previous page is the last real one.
 */
export function pageOffsets({ limit, offset, total }: PageMeta): PageOffsets {
  const lastPageOffset = total === 0 ? 0 : Math.floor((total - 1) / limit) * limit;
  const isPastEnd = offset >= total;

  return {
    firstRow: isPastEnd ? 0 : offset + 1,
    lastRow: isPastEnd ? 0 : Math.min(offset + limit, total),
    previousOffset:
      offset > 0 ? Math.max(0, Math.min(offset - limit, lastPageOffset)) : null,
    nextOffset: offset + limit < total ? offset + limit : null,
  };
}
