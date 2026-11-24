import {
  createColumnHelper,
  tableFeatures,
  type ColumnHelper,
  type RowData,
} from '@tanstack/react-table';

/**
 * @description The table features every roster uses: the core row model only. The API
 * pages and orders the rows, so nothing sorts, filters or pages them here.
 */
export const ROSTER_FEATURES = tableFeatures({});

export type RosterFeatures = typeof ROSTER_FEATURES;

/** @description The columns a roster of `Row` takes, built with `rosterColumnHelper`. */
export type RosterColumns<Row extends RowData> = ReturnType<
  ColumnHelper<RosterFeatures, Row>['columns']
>;

/**
 * @description A column helper for a roster of `Row`.
 * @note Give each column a string `header`: the phone layout labels each cell with it.
 * @example
 * ```ts
 * const helper = rosterColumnHelper<MobileSuitCardEntity>();
 * const columns = helper.columns([helper.accessor('name', { header: 'Name' })]);
 * ```
 */
export function rosterColumnHelper<Row extends RowData>(): ColumnHelper<
  RosterFeatures,
  Row
> {
  return createColumnHelper<RosterFeatures, Row>();
}
