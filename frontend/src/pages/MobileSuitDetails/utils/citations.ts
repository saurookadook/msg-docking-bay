import type { MobileSuitDetailEntity, SourceCitationEntity } from '@/api';

/** @description Renders the footnote mark for a fact's source. */
export type Cite = (source: SourceCitationEntity) => React.ReactElement;

/** @description The `idPrefix` linking the dossier's marks to its source list. */
export const SOURCE_ID_PREFIX = 'mobile-suit-source';

/**
 * @description Every source the dossier cites, in the order its sections show them:
 * the infobox's credits, then the spec sheets, the lineage and the appearances.
 * @note Duplicates stay; `numberCitations` numbers each distinct source once.
 */
export function collectCitations({
  appearances,
  designers,
  organizations,
  pilots,
  relations,
  spec_sheets,
}: MobileSuitDetailEntity): SourceCitationEntity[] {
  return [
    ...designers,
    ...organizations,
    ...pilots,
    ...spec_sheets,
    ...relations,
    ...appearances,
  ].map(({ source }) => source);
}
