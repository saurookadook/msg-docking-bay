import type { SourceCitationEntity } from '@/api';
import { numberCitations } from '@/utils';

import { CitationMark, type Cite } from '.';

/**
 * @description Numbers a page's sources in reading order (`numberCitations`), and builds
 * the `cite` that renders each fact's `CitationMark` against that page's
 * `SourceCitations`.
 * @returns the distinct sources, for `SourceCitations`, and `cite`
 */
export function numberedCitations({
  idPrefix,
  sources,
}: {
  /** @description The `idPrefix` of the page's `SourceCitations`. */
  idPrefix: string;
  sources: readonly SourceCitationEntity[];
}): { citations: SourceCitationEntity[]; cite: Cite } {
  const { citations, numberOf } = numberCitations(sources);
  return {
    citations,
    cite: (source) => <CitationMark idPrefix={idPrefix} number={numberOf(source)} />,
  };
}
