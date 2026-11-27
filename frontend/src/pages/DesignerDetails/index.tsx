import { useParams } from 'react-router';

import type { MechanicalDesignerDetailEntity, SourceCitationEntity } from '@/api';
import {
  CatalogDetail,
  CitationMark,
  DossierHeader,
  DossierLayout,
  DossierStrip,
  SourceCitations,
  SpecPlate,
  VisualSlot,
} from '@/components';
import { NotFound } from '@/pages/NotFound';
import { fetchMechanicalDesigner, useCatalogDetail, type AppState } from '@/store';
import type { AppParams } from '@/types';
import { numberCitations } from '@/utils';

import { DesignedUnits } from './components';
import { useDesignedUnits } from './utils/hooks';

const selectDesignerDetails = (appState: AppState) =>
  appState.mechanicalDesigners.detailsBySlug;

const PAGE_ID = 'designer-details';
const HEADING_ID = `${PAGE_ID}-title`;
const INFOBOX_HEADING_ID = `${PAGE_ID}-infobox-title`;
const SOURCE_ID_PREFIX = 'designer-source';
const FRAMING = 'Engineering credits';

/** @description Profile rows the catalog does not hold yet ("DATA PENDING"). */
const PENDING_ITEMS = [
  { label: 'Born', value: null },
  { label: 'Studio', value: null },
];

/** @description The engineering credits for a loaded designer. */
function EngineeringCredits({
  designer,
}: {
  designer: MechanicalDesignerDetailEntity;
}) {
  const designed = useDesignedUnits(designer.slug);
  // NOTE: the detail carries no source; each credit on this page of suits does.
  const { citations, numberOf } = numberCitations(
    designed.items.map(({ source }) => source),
  );
  const cite = (source: SourceCitationEntity) => (
    <CitationMark idPrefix={SOURCE_ID_PREFIX} number={numberOf(source)} />
  );

  return (
    <DossierLayout
      header={
        <DossierHeader
          classLine="Mechanical designer"
          eyebrow={FRAMING}
          headingID={HEADING_ID}
          name={designer.name}
          nameJa={designer.name_ja}
        />
      }
      headingID={HEADING_ID}
      id={PAGE_ID}
      infobox={
        <aside aria-labelledby={INFOBOX_HEADING_ID}>
          <VisualSlot subject={designer.name} />
          <h3 className="visually-hidden" id={INFOBOX_HEADING_ID}>
            Designer data
          </h3>
          <SpecPlate aria-label="Profile" isCompact items={PENDING_ITEMS} />
        </aside>
      }
      strip={<DossierStrip eyebrow={FRAMING} name={designer.name} />}
    >
      <DesignedUnits cite={cite} list={designed} />
      <SourceCitations citations={citations} idPrefix={SOURCE_ID_PREFIX} />
    </DossierLayout>
  );
}

/**
 * @description A mechanical designer's engineering credits, read from
 * `/mechanical-designers/:mechanicalDesignerSlug`. An old slug is swapped in the URL for
 * the designer's current one, keeping the search.
 */
export function DesignerDetails() {
  const { mechanicalDesignerSlug = '' } = useParams<AppParams>();
  const detailState = useCatalogDetail({
    fetchDetail: fetchMechanicalDesigner,
    selectDetails: selectDesignerDetails,
    slug: mechanicalDesignerSlug,
  });

  return (
    <CatalogDetail
      detailState={detailState}
      id={PAGE_ID}
      kind="mechanicalDesigner"
      loadingHeading={FRAMING}
      loadingLabel="Pulling the credits"
      notFound={<NotFound />}
      slug={mechanicalDesignerSlug}
    >
      {(designer) => <EngineeringCredits designer={designer} />}
    </CatalogDetail>
  );
}
