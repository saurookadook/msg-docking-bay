import type { DesignedMobileSuitEntity } from '@/api';
import {
  DetailSection,
  mobileSuitColumns,
  RosterBody,
  rosterColumnHelper,
  type Cite,
  type RosterColumns,
} from '@/components';
import type { ListState } from '@/store';
import { citationKey } from '@/utils';

const helper = rosterColumnHelper<DesignedMobileSuitEntity>();

/** @description The designed units' columns, with each credit cited. */
function designedColumns(cite: Cite): RosterColumns<DesignedMobileSuitEntity> {
  return [
    ...mobileSuitColumns<DesignedMobileSuitEntity>({
      marks: ({ source }) => cite(source),
      suitOf: ({ mobile_suit }) => mobile_suit,
    }),
    ...helper.columns([
      helper.accessor(({ mobile_suit }) => mobile_suit.continuity?.name ?? '—', {
        header: 'Continuity',
        id: 'continuity',
      }),
    ]),
  ];
}

/** @description A credit's row key: one suit can be credited by two sources. */
function creditRowID({ mobile_suit, source }: DesignedMobileSuitEntity): string {
  return `${mobile_suit.slug}|${citationKey(source)}`;
}

export type DesignedUnitsProps = {
  cite: Cite;
  list: ListState<DesignedMobileSuitEntity>;
};

/** @description The mobile weapons credited to the designer, by name, paged in `?offset=`. */
export function DesignedUnits({ cite, list }: DesignedUnitsProps) {
  return (
    <DetailSection className="designed-units" title="Designed units">
      <RosterBody
        caption="Mobile weapons credited to this designer, by name"
        columns={designedColumns(cite)}
        emptyState={<p>None on file</p>}
        getRowID={creditRowID}
        list={list}
      />
    </DetailSection>
  );
}
