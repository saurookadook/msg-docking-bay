import { useId } from 'react';

import type { MobileSuitAppearanceCardEntity } from '@/api';
import { EntityLink, RosterBody, rosterColumnHelper, StatusLamp } from '@/components';
import { UNIT_TYPE_LABELS } from '@/constants';
import type { ListState } from '@/store';
import { formatEpisodes } from '@/utils';

const helper = rosterColumnHelper<MobileSuitAppearanceCardEntity>();

const columns = helper.columns([
  helper.accessor(({ model_number }) => model_number ?? '—', {
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
  helper.accessor(({ unit_type }) => UNIT_TYPE_LABELS[unit_type], {
    header: 'Unit type',
    id: 'unit_type',
  }),
  helper.accessor((suit) => formatEpisodes(suit) ?? '—', {
    header: 'Episodes',
    id: 'episodes',
  }),
  helper.accessor('is_debut', {
    cell: ({ getValue }) =>
      getValue() ? <StatusLamp status="online">Debut</StatusLamp> : '—',
    header: 'Debut',
  }),
]);

export type WorkSuitsProps = {
  list: ListState<MobileSuitAppearanceCardEntity>;
};

/** @description The mobile weapons appearing in the work, debuts first, paged in `?offset=`. */
export function WorkSuits({ list }: WorkSuitsProps) {
  const headingID = useId();

  return (
    <section aria-labelledby={headingID} className="work-suits">
      <h3 className="stencil-label" id={headingID}>
        Mobile weapons appearing
      </h3>
      <RosterBody
        caption="Mobile weapons in this work, debuts first"
        columns={columns}
        emptyState={<p>None on file</p>}
        list={list}
      />
    </section>
  );
}
