import { useParams } from 'react-router';

import type { WorkDetailEntity } from '@/api';
import {
  CatalogDetail,
  DossierHeader,
  DossierLayout,
  DossierStrip,
  EntityLink,
  numberedCitations,
  PendingSection,
  SourceCitations,
  SpecPlate,
  VisualSlot,
} from '@/components';
import { WORK_TYPE_LABELS } from '@/constants';
import { NotFound } from '@/pages/NotFound';
import { fetchWork, useCatalogDetail, type AppState } from '@/store';
import type { AppParams } from '@/types';
import { joinParts } from '@/utils';

import { RelatedWorks, WorkSuits } from './components';
import { formatWorkDates, workDatesLabel } from './utils/dates';
import { useWorkSuits } from './utils/hooks';

const selectWorkDetails = (appState: AppState) => appState.works.detailsBySlug;

const PAGE_ID = 'work-details';
const HEADING_ID = `${PAGE_ID}-title`;
const INFOBOX_HEADING_ID = `${PAGE_ID}-infobox-title`;
const SOURCE_ID_PREFIX = 'work-source';
const FRAMING = 'Operation log';

/** @description Wiki sections the catalog does not hold yet. */
const PENDING_SECTIONS = ['Staff', 'Characters', 'Plot'];

/** @description The operation log for a loaded work. */
function OperationLog({ work }: { work: WorkDetailEntity }) {
  const suitList = useWorkSuits(work.slug);
  // NOTE: only relations are cited; the work's suit list carries no sources.
  const { citations, cite } = numberedCitations({
    idPrefix: SOURCE_ID_PREFIX,
    sources: work.relations.map(({ source }) => source),
  });
  const { continuity, parent_work, title, title_ja, work_type } = work;

  return (
    <DossierLayout
      header={
        <DossierHeader
          classLine={joinParts([WORK_TYPE_LABELS[work_type], continuity?.name])}
          eyebrow={FRAMING}
          headingID={HEADING_ID}
          name={title}
          nameJa={title_ja}
        />
      }
      headingID={HEADING_ID}
      id={PAGE_ID}
      infobox={
        <aside aria-labelledby={INFOBOX_HEADING_ID}>
          <VisualSlot shape="landscape" subject={title} />
          <h3 className="visually-hidden" id={INFOBOX_HEADING_ID}>
            Operation data
          </h3>
          <SpecPlate
            aria-label="Log"
            isCompact
            items={[
              { label: 'Type', value: WORK_TYPE_LABELS[work_type] },
              { label: workDatesLabel(work_type), value: formatWorkDates(work) },
              { label: 'Continuity', value: continuity?.name ?? null },
              {
                label: 'Part of',
                value:
                  parent_work == null ? (
                    'None on file'
                  ) : (
                    <EntityLink kind="work" slug={parent_work.slug}>
                      {parent_work.title}
                    </EntityLink>
                  ),
              },
              { label: 'Studio', value: null },
              { label: 'Episodes', value: null },
            ]}
          />
        </aside>
      }
      strip={<DossierStrip eyebrow={FRAMING} name={title} />}
    >
      <RelatedWorks cite={cite} relations={work.relations} />
      <WorkSuits list={suitList} />
      {PENDING_SECTIONS.map((pendingTitle) => (
        <PendingSection key={pendingTitle} title={pendingTitle} />
      ))}
      <SourceCitations citations={citations} idPrefix={SOURCE_ID_PREFIX} />
    </DossierLayout>
  );
}

/**
 * @description A work's operation log, read from `/works/:workSlug`. An old slug is
 * swapped in the URL for the work's current one, keeping the search.
 */
export function WorkDetails() {
  const { workSlug = '' } = useParams<AppParams>();
  const detailState = useCatalogDetail({
    fetchDetail: fetchWork,
    selectDetails: selectWorkDetails,
    slug: workSlug,
  });

  return (
    <CatalogDetail
      detailState={detailState}
      id={PAGE_ID}
      kind="work"
      loadingHeading={FRAMING}
      loadingLabel="Opening the log"
      notFound={<NotFound />}
      slug={workSlug}
    >
      {(work) => <OperationLog work={work} />}
    </CatalogDetail>
  );
}
