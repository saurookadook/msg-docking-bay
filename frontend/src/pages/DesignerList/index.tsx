import type { MechanicalDesignerCardEntity } from '@/api';
import { CatalogRoster, EntityLink, FilterBar, rosterColumnHelper } from '@/components';
import { fetchMechanicalDesigners, useCatalogList, type AppState } from '@/store';

const LIST_KEYS = ['limit', 'offset', 'q'] as const;

const selectMechanicalDesigners = (appState: AppState) =>
  appState.mechanicalDesigners.list;

const helper = rosterColumnHelper<MechanicalDesignerCardEntity>();

const columns = helper.columns([
  helper.accessor('name', {
    cell: ({ row }) => (
      <EntityLink kind="mechanicalDesigner" slug={row.original.slug}>
        {row.original.name}
      </EntityLink>
    ),
    header: 'Name',
  }),
  helper.accessor('name_ja', {
    cell: ({ getValue }) => <span lang="ja">{getValue() ?? '—'}</span>,
    header: 'Japanese name',
  }),
]);

/** @description The engineering credits, read from `/mechanical-designers?q=`. */
export function DesignerList() {
  const list = useCatalogList({
    fetchList: fetchMechanicalDesigners,
    keys: LIST_KEYS,
    selectList: selectMechanicalDesigners,
  });

  return (
    <CatalogRoster
      caption="Mechanical designers, by name"
      columns={columns}
      eyebrow="ENGINEERING CREDITS"
      filterBar={<FilterBar searchLabel="Search designers" />}
      heading="Designers"
      id="designer-list"
      list={list}
      rowHeaderColumnID="name"
    />
  );
}
