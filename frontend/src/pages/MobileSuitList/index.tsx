import { useMemo } from 'react';

import type { MobileSuitCardEntity } from '@/api';
import {
  CageNumber,
  CatalogRoster,
  EntityLink,
  FilterBar,
  rosterColumnHelper,
} from '@/components';
import { UNIT_TYPE_LABELS, UNIT_TYPE_OPTIONS } from '@/constants';
import {
  fetchMobileSuits,
  useCatalogList,
  useContinuityOptions,
  useWorkFilterChips,
  type AppState,
} from '@/store';

const LIST_KEYS = ['continuity', 'limit', 'offset', 'q', 'unit_type', 'work'] as const;

const selectMobileSuits = (appState: AppState) => appState.mobileSuits.list;

/** @description The deck the suits are kept on, shown in the heading and each cage. */
const SUIT_DECK = 1;

const helper = rosterColumnHelper<MobileSuitCardEntity>();

/**
 * @description The suits roster, read from `/mobile-suits?continuity=&unit_type=&work=&q=`.
 */
export function MobileSuitList() {
  const list = useCatalogList({
    fetchList: fetchMobileSuits,
    keys: LIST_KEYS,
    selectList: selectMobileSuits,
  });
  const continuityOptions = useContinuityOptions();
  const workChips = useWorkFilterChips();
  const offset = list.meta?.offset ?? 0;

  // NOTE: memoized on offset, so the table gets new columns only when the page changes.
  const columns = useMemo(
    () =>
      helper.columns([
        helper.display({
          cell: ({ row }) => (
            <CageNumber cage={offset + row.index + 1} deck={SUIT_DECK} />
          ),
          header: 'Cage',
          id: 'cage',
        }),
        helper.accessor((suit) => suit.model_number ?? '—', {
          header: 'Model number',
          id: 'model_number',
        }),
        helper.accessor('name', {
          cell: ({ row }) => (
            <EntityLink kind="mobileSuit" slug={row.original.slug}>
              {row.original.name}
            </EntityLink>
          ),
          header: 'Name',
          meta: { isRowHeader: true },
        }),
        helper.accessor('unit_type', {
          cell: ({ getValue }) => UNIT_TYPE_LABELS[getValue()],
          header: 'Unit type',
        }),
        helper.accessor((suit) => suit.continuity?.name ?? '—', {
          header: 'Continuity',
          id: 'continuity',
        }),
      ]),
    [offset],
  );

  return (
    <CatalogRoster
      caption="Mobile suits in their cages, by name"
      columns={columns}
      eyebrow={`MS DECK ${String(SUIT_DECK).padStart(2, '0')}`}
      filterBar={
        <FilterBar
          chips={workChips}
          searchLabel="Search mobile suits"
          selects={[
            {
              label: 'Continuity',
              options: continuityOptions,
              param: 'continuity',
            },
            { label: 'Unit type', options: UNIT_TYPE_OPTIONS, param: 'unit_type' },
          ]}
        />
      }
      heading="Mobile Suits"
      id="mobile-suit-list"
      list={list}
    />
  );
}
