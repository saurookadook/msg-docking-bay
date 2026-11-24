import type { WorkCardEntity } from '@/api';
import { CatalogRoster, EntityLink, FilterBar, rosterColumnHelper } from '@/components';
import { WORK_TYPE_LABELS } from '@/constants';
import { fetchWorks, useCatalogList, useContinuities, type AppState } from '@/store';

const LIST_KEYS = ['continuity', 'limit', 'offset', 'q', 'work_type'] as const;

const WORK_TYPE_OPTIONS = Object.entries(WORK_TYPE_LABELS).map(([value, label]) => ({
  label,
  value,
}));

const selectWorks = (appState: AppState) => appState.works.list;

/** @description A work's run: `start – end`, the start alone, or a dash. */
function formatRun({ end_date, start_date }: WorkCardEntity): string {
  if (start_date == null) return '—';
  return end_date == null || end_date === start_date
    ? start_date
    : `${start_date} – ${end_date}`;
}

const helper = rosterColumnHelper<WorkCardEntity>();

const columns = helper.columns([
  helper.accessor('title', {
    cell: ({ row }) => (
      <EntityLink kind="work" slug={row.original.slug}>
        {row.original.title}
      </EntityLink>
    ),
    header: 'Title',
  }),
  helper.accessor('work_type', {
    cell: ({ getValue }) => WORK_TYPE_LABELS[getValue()],
    header: 'Type',
  }),
  helper.accessor(formatRun, { header: 'Released', id: 'released' }),
  helper.accessor((work) => work.continuity?.name ?? '—', {
    header: 'Continuity',
    id: 'continuity',
  }),
]);

/** @description The operation logs, read from `/works?continuity=&work_type=&q=`. */
export function WorkList() {
  const list = useCatalogList({
    fetchList: fetchWorks,
    keys: LIST_KEYS,
    selectList: selectWorks,
  });
  const { continuities } = useContinuities();

  return (
    <CatalogRoster
      caption="Works, first released first"
      columns={columns}
      eyebrow="OPERATION LOGS"
      filterBar={
        <FilterBar
          searchLabel="Search works"
          selects={[
            {
              label: 'Continuity',
              options: continuities.map(({ name, slug }) => ({
                label: name,
                value: slug,
              })),
              param: 'continuity',
            },
            { label: 'Type', options: WORK_TYPE_OPTIONS, param: 'work_type' },
          ]}
        />
      }
      heading="Works"
      id="work-list"
      list={list}
      rowHeaderColumnID="title"
    />
  );
}
