import type { OrganizationCardEntity } from '@/api';
import { CatalogRoster, EntityLink, FilterBar, rosterColumnHelper } from '@/components';
import {
  fetchOrganizations,
  useCatalogList,
  useWorkFilterChips,
  type AppState,
} from '@/store';

const LIST_KEYS = ['limit', 'offset', 'q', 'work'] as const;

const selectOrganizations = (appState: AppState) => appState.organizations.list;

const helper = rosterColumnHelper<OrganizationCardEntity>();

const columns = helper.columns([
  helper.accessor('name', {
    cell: ({ row }) => (
      <EntityLink kind="organization" slug={row.original.slug}>
        {row.original.name}
      </EntityLink>
    ),
    header: 'Name',
  }),
  helper.accessor('parent_organization', {
    cell: ({ getValue }) => {
      const parent = getValue();
      return parent == null ? (
        '—'
      ) : (
        <EntityLink kind="organization" slug={parent.slug}>
          {parent.name}
        </EntityLink>
      );
    },
    header: 'Parent',
  }),
]);

/** @description The faction registry, read from `/organizations?work=&q=`. */
export function OrganizationList() {
  const list = useCatalogList({
    fetchList: fetchOrganizations,
    keys: LIST_KEYS,
    selectList: selectOrganizations,
  });
  const workChips = useWorkFilterChips();

  return (
    <CatalogRoster
      caption="Organizations, by name"
      columns={columns}
      eyebrow="FACTION REGISTRY"
      filterBar={<FilterBar chips={workChips} searchLabel="Search organizations" />}
      heading="Organizations"
      id="organization-list"
      list={list}
      rowHeaderColumnID="name"
    />
  );
}
