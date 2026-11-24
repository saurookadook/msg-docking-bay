import { useId, useMemo } from 'react';
import { Navigate, useLocation, useParams } from 'react-router';

import type { MobileSuitDetailEntity, SourceCitationEntity } from '@/api';
import {
  CitationMark,
  DeckPanel,
  numberCitations,
  SourceCitations,
  SpecPlate,
  StatusLamp,
} from '@/components';
import { NotFound } from '@/pages/NotFound';
import { fetchMobileSuit, useCatalogDetail, type AppState } from '@/store';
import type { AppParams } from '@/types';
import { entityPath } from '@/utils';

import {
  SpecSheetTabs,
  SuitAppearances,
  SuitHeader,
  SuitInfobox,
  SuitLineage,
  SuitStrip,
} from './components';
import { collectCitations, SOURCE_ID_PREFIX } from './utils/citations';
import { useSelectedSpecSheet } from './utils/hooks';

import './styles.css';

const selectMobileSuitDetails = (appState: AppState) =>
  appState.mobileSuits.detailsBySlug;

const HEADING_ID = 'mobile-suit-details-title';

/** @description Infobox rows the catalog does not hold yet ("DATA PENDING"). */
const REGISTRY_ITEMS = [
  { label: 'Other names', value: null },
  { label: 'Archetype', value: null },
  { label: 'Production', value: null },
];

/** @description Wiki sections the catalog does not hold yet. */
const PENDING_SECTIONS = ['History', 'Gallery', 'Trivia'];

/** @description A section shown as an empty slot until its data is ingested. */
function PendingSection({ title }: { title: string }) {
  const headingID = useId();
  return (
    <section aria-labelledby={headingID} className="pending-section">
      <h3 className="stencil-label" id={headingID}>
        {title}
      </h3>
      <DeckPanel>
        <p className="stencil-label">DATA PENDING</p>
      </DeckPanel>
    </section>
  );
}

/** @description The dossier for a loaded suit. */
function Dossier({ suit }: { suit: MobileSuitDetailEntity }) {
  const selected = useSelectedSpecSheet(suit.spec_sheets);
  const { index, labels, sheet } = selected;
  const { citations, numberOf } = useMemo(
    () => numberCitations(collectCitations(suit)),
    [suit],
  );
  const cite = (source: SourceCitationEntity) => (
    <CitationMark idPrefix={SOURCE_ID_PREFIX} number={numberOf(source)} />
  );

  return (
    <article aria-labelledby={HEADING_ID} id="mobile-suit-details">
      <SuitStrip suit={suit} />
      <SuitHeader headingID={HEADING_ID} suit={suit} />
      <SuitInfobox
        cite={cite}
        sheet={sheet}
        sheetLabel={labels[index] ?? null}
        suit={suit}
      />
      <div className="mobile-suit-details-body">
        <SpecPlate
          aria-label="Registry"
          className="registry-plate"
          items={REGISTRY_ITEMS}
        />
        <SpecSheetTabs
          cite={cite}
          name={suit.name}
          selected={selected}
          sheets={suit.spec_sheets}
        />
        <SuitLineage cite={cite} suit={suit} />
        <SuitAppearances appearances={suit.appearances} cite={cite} />
        {PENDING_SECTIONS.map((title) => (
          <PendingSection key={title} title={title} />
        ))}
        <SourceCitations citations={citations} idPrefix={SOURCE_ID_PREFIX} />
      </div>
    </article>
  );
}

/**
 * @description A mobile suit's maintenance dossier, read from `/mobile-suits/:mobileSuitSlug`.
 * An old slug is swapped in the URL for the suit's current one, keeping the search.
 */
export function MobileSuitDetails() {
  const { mobileSuitSlug = '' } = useParams<AppParams>();
  const { search } = useLocation();
  const detailState = useCatalogDetail({
    fetchDetail: fetchMobileSuit,
    selectDetails: selectMobileSuitDetails,
    slug: mobileSuitSlug,
  });
  const suit = detailState?.detail ?? null;

  if (detailState?.isNotFound === true) return <NotFound />;

  if (suit != null && suit.slug !== mobileSuitSlug) {
    return (
      <Navigate
        replace
        to={{ pathname: entityPath({ kind: 'mobileSuit', slug: suit.slug }), search }}
      />
    );
  }

  if (suit != null) return <Dossier suit={suit} />;

  return (
    <section aria-label="Mobile suit dossier" id="mobile-suit-details">
      <p role="status">
        {detailState?.errorMessage == null && (
          <StatusLamp status="busy">Opening the dossier</StatusLamp>
        )}
      </p>
      {detailState?.errorMessage != null && (
        <p role="alert">{detailState.errorMessage}</p>
      )}
    </section>
  );
}
