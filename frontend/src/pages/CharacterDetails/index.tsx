import { useParams } from 'react-router';

import type { CharacterDetailEntity, SourceCitationEntity } from '@/api';
import {
  CatalogDetail,
  CitationMark,
  DossierHeader,
  DossierLayout,
  DossierStrip,
  PendingSection,
  SourceCitations,
  SpecPlate,
  VisualSlot,
  WorkAppearances,
} from '@/components';
import { NotFound } from '@/pages/NotFound';
import { fetchCharacter, useCatalogDetail, type AppState } from '@/store';
import type { AppParams } from '@/types';
import { numberCitations } from '@/utils';

import { QualifiedUnits } from './components';
import { collectCitations, SOURCE_ID_PREFIX } from './utils/citations';

const selectCharacterDetails = (appState: AppState) =>
  appState.characters.detailsBySlug;

const PAGE_ID = 'character-details';
const HEADING_ID = `${PAGE_ID}-title`;
const INFOBOX_HEADING_ID = `${PAGE_ID}-infobox-title`;
const FRAMING = 'Personnel file';

/** @description ID card rows the catalog does not hold yet ("DATA PENDING"). */
const REGISTRY_ITEMS = [
  { label: 'Affiliation', value: null },
  { label: 'Rank', value: null },
  { label: 'Gender', value: null },
  { label: 'Age', value: null },
  { label: 'Voice actors', value: null },
];

/** @description Wiki sections the catalog does not hold yet. */
const PENDING_SECTIONS = [
  'Personality',
  'Skills',
  'History',
  'Relationships',
  'Quotes',
];

/**
 * @description The continuities a character appears in, in the order of their works, as
 * the header's class line.
 */
function continuityLine({ appearances }: CharacterDetailEntity): string {
  const names = appearances.flatMap(({ work }) =>
    work.continuity == null ? [] : [work.continuity.name],
  );
  return names.length === 0 ? 'Personnel' : [...new Set(names)].join(' · ');
}

/** @description The personnel file for a loaded character. */
function PersonnelFile({ character }: { character: CharacterDetailEntity }) {
  const { citations, numberOf } = numberCitations(collectCitations(character));
  const cite = (source: SourceCitationEntity) => (
    <CitationMark idPrefix={SOURCE_ID_PREFIX} number={numberOf(source)} />
  );

  return (
    <DossierLayout
      header={
        <DossierHeader
          classLine={continuityLine(character)}
          eyebrow={FRAMING}
          headingID={HEADING_ID}
          name={character.name}
          nameJa={character.name_ja}
        />
      }
      headingID={HEADING_ID}
      id={PAGE_ID}
      infobox={
        <aside aria-labelledby={INFOBOX_HEADING_ID}>
          <VisualSlot subject={character.name} />
          <h3 className="visually-hidden" id={INFOBOX_HEADING_ID}>
            Personnel data
          </h3>
          <SpecPlate aria-label="ID card" isCompact items={REGISTRY_ITEMS} />
        </aside>
      }
      strip={<DossierStrip eyebrow={FRAMING} name={character.name} />}
    >
      <QualifiedUnits cite={cite} piloted={character.piloted_mobile_suits} />
      <WorkAppearances appearances={character.appearances} cite={cite} />
      {PENDING_SECTIONS.map((title) => (
        <PendingSection key={title} title={title} />
      ))}
      <SourceCitations citations={citations} idPrefix={SOURCE_ID_PREFIX} />
    </DossierLayout>
  );
}

/**
 * @description A character's personnel file, read from `/characters/:characterSlug`. An
 * old slug is swapped in the URL for the character's current one, keeping the search.
 */
export function CharacterDetails() {
  const { characterSlug = '' } = useParams<AppParams>();
  const detailState = useCatalogDetail({
    fetchDetail: fetchCharacter,
    selectDetails: selectCharacterDetails,
    slug: characterSlug,
  });

  return (
    <CatalogDetail
      detailState={detailState}
      id={PAGE_ID}
      kind="character"
      loadingHeading={FRAMING}
      loadingLabel="Pulling the personnel file"
      notFound={<NotFound />}
      slug={characterSlug}
    >
      {(character) => <PersonnelFile character={character} />}
    </CatalogDetail>
  );
}
