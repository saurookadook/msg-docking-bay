import type { DesignedMobileSuitEntity } from '@/api';
import {
  DetailSection,
  EntityLink,
  RosterBody,
  rosterColumnHelper,
  type Cite,
  type RosterColumns,
} from '@/components';
import { UNIT_TYPE_LABELS } from '@/constants';
import type { ListState } from '@/store';
import { citationKey } from '@/utils';

const helper = rosterColumnHelper<DesignedMobileSuitEntity>();

/** @description The designed units' columns, with each credit cited. */
function designedColumns(cite: Cite): RosterColumns<DesignedMobileSuitEntity> {
  return helper.columns([
    helper.accessor(({ mobile_suit }) => mobile_suit.model_number ?? '—', {
      header: 'Model number',
      id: 'model_number',
    }),
    helper.accessor(({ mobile_suit }) => mobile_suit.name, {
      cell: ({ getValue, row }) => (
        <>
          <EntityLink kind="mobileSuit" slug={row.original.mobile_suit.slug}>
            {getValue()}
          </EntityLink>
          {cite(row.original.source)}
        </>
      ),
      header: 'Name',
      id: 'name',
      meta: { isRowHeader: true },
    }),
    helper.accessor(({ mobile_suit }) => UNIT_TYPE_LABELS[mobile_suit.unit_type], {
      header: 'Unit type',
      id: 'unit_type',
    }),
    helper.accessor(({ mobile_suit }) => mobile_suit.continuity?.name ?? '—', {
      header: 'Continuity',
      id: 'continuity',
    }),
  ]);
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
