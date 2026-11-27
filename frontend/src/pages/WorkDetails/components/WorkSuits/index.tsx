import type { MobileSuitAppearanceCardEntity } from '@/api';
import {
  DetailSection,
  mobileSuitColumns,
  RosterBody,
  rosterColumnHelper,
  StatusLamp,
} from '@/components';
import type { ListState } from '@/store';
import { formatEpisodes } from '@/utils';

const helper = rosterColumnHelper<MobileSuitAppearanceCardEntity>();

const columns = [
  ...mobileSuitColumns<MobileSuitAppearanceCardEntity>({ suitOf: (suit) => suit }),
  ...helper.columns([
    helper.accessor((suit) => formatEpisodes(suit) ?? '—', {
      header: 'Episodes',
      id: 'episodes',
    }),
    helper.accessor('is_debut', {
      cell: ({ getValue }) =>
        getValue() ? <StatusLamp status="online">Debut</StatusLamp> : '—',
      header: 'Debut',
    }),
  ]),
];

export type WorkSuitsProps = {
  list: ListState<MobileSuitAppearanceCardEntity>;
};

/** @description The mobile weapons appearing in the work, debuts first, paged in `?offset=`. */
export function WorkSuits({ list }: WorkSuitsProps) {
  return (
    <DetailSection className="work-suits" title="Mobile weapons appearing">
      <RosterBody
        caption="Mobile weapons in this work, debuts first"
        columns={columns}
        emptyState={<p>None on file</p>}
        list={list}
      />
    </DetailSection>
  );
}
