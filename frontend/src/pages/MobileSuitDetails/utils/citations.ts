import type { MobileSuitDetailEntity, SourceCitationEntity } from '@/api';

/** @description The `idPrefix` linking the dossier's marks to its source list. */
export const SOURCE_ID_PREFIX = 'mobile-suit-source';

/**
 * @description Every source the dossier cites, in the order a reader meets them: the
 * spec sheets (the infobox names the selected one first), then the infobox's credits,
 * the lineage and the appearances.
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
    ...spec_sheets,
    ...designers,
    ...organizations,
    ...pilots,
    ...relations,
    ...appearances,
  ].map(({ source }) => source);
}
