// The API's `q` matching (D8 in `docs/plans/catalog-read-api.md`), for mock mode. The
// backend's copy is `normalize_search` and the `BaseFacade` search helpers in
// `backend/models/base/facade.py`; change both.
import type { Nullable } from '@/types';

/**
 * @description Lowercases `q` and keeps only `a-z0-9`, as the API does: `RX 78-2` and
 * `rx-78-2` both become `rx782`.
 * @returns The needle, or `undefined` when nothing is left, which means no filter.
 */
export function normalizeSearch(q: Nullable<string> | undefined): string | undefined {
  if (q == null) return undefined;
  return q.toLowerCase().replaceAll(/[^a-z0-9]/g, '') || undefined;
}

/**
 * @description Filters `items` to those where any of `columns` contains the normalized
 * `q`, with prefix matches first, as a list route's `q` does. The sort is stable, so the
 * rest keep the order `items` came in: the route's list order.
 * @returns `items` unchanged when `q` is blank after normalization.
 */
export function searchList<T>({
  columns,
  items,
  q,
}: {
  columns: (item: T) => readonly (Nullable<string> | undefined)[];
  items: readonly T[];
  q: Nullable<string> | undefined;
}): readonly T[] {
  const needle = normalizeSearch(q);
  if (needle === undefined) return items;
  const normalized = (item: T): string[] =>
    columns(item).map((column) => normalizeSearch(column) ?? '');
  return items
    .filter((item) => normalized(item).some((column) => column.includes(needle)))
    .toSorted(
      (a, b) =>
        Number(!normalized(a).some((column) => column.startsWith(needle))) -
        Number(!normalized(b).some((column) => column.startsWith(needle))),
    );
}
