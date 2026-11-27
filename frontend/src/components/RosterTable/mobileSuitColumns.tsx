import type { RowData } from '@tanstack/react-table';

import type { MobileSuitCardEntity } from '@/api';
import { EntityLink } from '@/components';
import { UNIT_TYPE_LABELS } from '@/constants';

import { rosterColumnHelper, type RosterColumns } from './rosterColumns';

/**
 * @description The columns every suit roster opens with: model number, the linked name
 * (the row header) and unit type, read from the row's suit.
 * @example
 * ```ts
 * const columns = [
 *   ...mobileSuitColumns<DesignedMobileSuitEntity>({
 *     marks: (row) => cite(row.source),
 *     suitOf: (row) => row.mobile_suit,
 *   }),
 *   ...helper.columns([continuityColumn]),
 * ];
 * ```
 */
export function mobileSuitColumns<Row extends RowData>({
  marks,
  suitOf,
}: {
  /** @description What follows the name in its cell, such as footnote marks. */
  marks?: (row: Row) => React.ReactNode;
  suitOf: (row: Row) => MobileSuitCardEntity;
}): RosterColumns<Row> {
  const helper = rosterColumnHelper<Row>();
  return helper.columns([
    helper.accessor((row) => suitOf(row).model_number ?? '—', {
      header: 'Model number',
      id: 'model_number',
    }),
    helper.accessor((row) => suitOf(row).name, {
      cell: ({ getValue, row }) => (
        <>
          <EntityLink kind="mobileSuit" slug={suitOf(row.original).slug}>
            {getValue()}
          </EntityLink>
          {marks?.(row.original)}
        </>
      ),
      header: 'Name',
      id: 'name',
      meta: { isRowHeader: true },
    }),
    helper.accessor((row) => UNIT_TYPE_LABELS[suitOf(row).unit_type], {
      header: 'Unit type',
      id: 'unit_type',
    }),
  ]);
}
