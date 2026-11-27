import type { CharacterDetailEntity, SourceCitationEntity } from '@/api';

/** @description The `idPrefix` linking the personnel file's marks to its source list. */
export const SOURCE_ID_PREFIX = 'character-source';

/**
 * @description Every source the personnel file cites, in the order a reader meets them:
 * the qualified units, then the appearances.
 * @note Duplicates stay; `numberCitations` numbers each distinct source once.
 */
export function collectCitations({
  appearances,
  piloted_mobile_suits,
}: CharacterDetailEntity): SourceCitationEntity[] {
  return [...piloted_mobile_suits, ...appearances].map(({ source }) => source);
}
