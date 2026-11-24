import {
  createColumnHelper,
  tableFeatures,
  type ColumnHelper,
  type RowData,
} from '@tanstack/react-table';

/** @description What a roster column can say about itself, on `columnDef.meta`. */
export type RosterColumnMeta = {
  /** @description Its cell names the row, as a `<th scope="row">`. Mark one column. */
  isRowHeader?: boolean;
};

/**
 * @description The table features every roster uses: the core row model only. The API
 * pages and orders the rows, so nothing sorts, filters or pages them here.
 * @note `columnMeta` only types each column's `meta` as `RosterColumnMeta`.
 */
export const ROSTER_FEATURES = tableFeatures({ columnMeta: {} as RosterColumnMeta });

export type RosterFeatures = typeof ROSTER_FEATURES;

/** @description The columns a roster of `Row` takes, built with `rosterColumnHelper`. */
export type RosterColumns<Row extends RowData> = ReturnType<
  ColumnHelper<RosterFeatures, Row>['columns']
>;

/**
 * @description A column helper for a roster of `Row`.
 * @note Give each column a string `header`: the phone layout labels each cell with it.
 * Mark the column that names the row with `meta: { isRowHeader: true }`.
 * @example
 * ```ts
 * const helper = rosterColumnHelper<MobileSuitCardEntity>();
 * const columns = helper.columns([
 *   helper.accessor('name', { header: 'Name', meta: { isRowHeader: true } }),
 * ]);
 * ```
 */
export function rosterColumnHelper<Row extends RowData>(): ColumnHelper<
  RosterFeatures,
  Row
> {
  return createColumnHelper<RosterFeatures, Row>();
}
