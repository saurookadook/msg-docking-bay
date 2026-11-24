import type { CharacterCardEntity } from '@/api';
import { CatalogRoster, EntityLink, FilterBar, rosterColumnHelper } from '@/components';
import {
  fetchCharacters,
  useCatalogList,
  useWorkFilterChips,
  type AppState,
} from '@/store';

const LIST_KEYS = ['limit', 'offset', 'q', 'work'] as const;

const selectCharacters = (appState: AppState) => appState.characters.list;

const helper = rosterColumnHelper<CharacterCardEntity>();

const columns = helper.columns([
  helper.accessor('name', {
    cell: ({ row }) => (
      <EntityLink kind="character" slug={row.original.slug}>
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

/** @description The personnel files, read from `/characters?work=&q=`. */
export function CharacterList() {
  const list = useCatalogList({
    fetchList: fetchCharacters,
    keys: LIST_KEYS,
    selectList: selectCharacters,
  });
  const workChips = useWorkFilterChips();

  return (
    <CatalogRoster
      caption="Personnel files, by name"
      columns={columns}
      eyebrow="CREW QUARTERS"
      filterBar={<FilterBar chips={workChips} searchLabel="Search personnel" />}
      heading="Personnel"
      id="character-list"
      list={list}
      rowHeaderColumnID="name"
    />
  );
}
