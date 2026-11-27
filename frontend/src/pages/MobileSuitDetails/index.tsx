import { useParams } from 'react-router';

import type { MobileSuitDetailEntity } from '@/api';
import {
  CatalogDetail,
  DossierHeader,
  DossierLayout,
  DossierStrip,
  numberedCitations,
  PendingSection,
  SourceCitations,
  SpecPlate,
  WorkAppearances,
} from '@/components';
import { UNIT_TYPE_LABELS } from '@/constants';
import { NotFound } from '@/pages/NotFound';
import { fetchMobileSuit, useCatalogDetail, type AppState } from '@/store';
import type { AppParams } from '@/types';

import { SpecSheetTabs, SuitInfobox, SuitLineage } from './components';
import { collectCitations, SOURCE_ID_PREFIX } from './utils/citations';
import { useSpecSheetSelection } from './utils/hooks';

const selectMobileSuitDetails = (appState: AppState) =>
  appState.mobileSuits.detailsBySlug;

const PAGE_ID = 'mobile-suit-details';
const HEADING_ID = `${PAGE_ID}-title`;

/** @description Infobox rows the catalog does not hold yet ("DATA PENDING"). */
const REGISTRY_ITEMS = [
  { label: 'Other names', value: null },
  { label: 'Archetype', value: null },
  { label: 'Production', value: null },
];

/** @description Wiki sections the catalog does not hold yet. */
const PENDING_SECTIONS = ['History', 'Gallery', 'Trivia'];

/** @description The dossier for a loaded suit. */
function Dossier({ suit }: { suit: MobileSuitDetailEntity }) {
  const selection = useSpecSheetSelection(suit.spec_sheets);
  const { citations, cite } = numberedCitations({
    idPrefix: SOURCE_ID_PREFIX,
    sources: collectCitations(suit),
  });
  const { continuity, model_number, name, name_ja, unit_type } = suit;

  return (
    <DossierLayout
      header={
        <DossierHeader
          classLine={[UNIT_TYPE_LABELS[unit_type], continuity?.name]
            .filter((part) => part != null)
            .join(' · ')}
          eyebrow={model_number ?? 'No model number'}
          headingID={HEADING_ID}
          name={name}
          nameJa={name_ja}
        />
      }
      headingID={HEADING_ID}
      id={PAGE_ID}
      infobox={<SuitInfobox cite={cite} selected={selection.selected} suit={suit} />}
      strip={<DossierStrip eyebrow={model_number} name={name} />}
    >
      <SpecPlate
        aria-label="Registry"
        className="registry-plate"
        items={REGISTRY_ITEMS}
      />
      <SpecSheetTabs cite={cite} name={suit.name} selection={selection} />
      <SuitLineage cite={cite} suit={suit} />
      <WorkAppearances appearances={suit.appearances} cite={cite} />
      {PENDING_SECTIONS.map((title) => (
        <PendingSection key={title} title={title} />
      ))}
      <SourceCitations citations={citations} idPrefix={SOURCE_ID_PREFIX} />
    </DossierLayout>
  );
}

/**
 * @description A mobile suit's maintenance dossier, read from `/mobile-suits/:mobileSuitSlug`.
 * An old slug is swapped in the URL for the suit's current one, keeping the search.
 */
export function MobileSuitDetails() {
  const { mobileSuitSlug = '' } = useParams<AppParams>();
  const detailState = useCatalogDetail({
    fetchDetail: fetchMobileSuit,
    selectDetails: selectMobileSuitDetails,
    slug: mobileSuitSlug,
  });

  return (
    <CatalogDetail
      detailState={detailState}
      id={PAGE_ID}
      kind="mobileSuit"
      loadingHeading="Mobile suit dossier"
      loadingLabel="Opening the dossier"
      notFound={<NotFound />}
      slug={mobileSuitSlug}
    >
      {(suit) => <Dossier suit={suit} />}
    </CatalogDetail>
  );
}
