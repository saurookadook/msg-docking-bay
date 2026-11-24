import type { SourceCitationEntity } from '@/api';

/**
 * @description What makes two citations the same source: the page and the revision used.
 * Two revisions of one page are two sources.
 */
export function citationKey({ kind, revision_id, url }: SourceCitationEntity): string {
  return `${kind}|${url}|${revision_id ?? ''}`;
}

/** @description The `id` of a citation's entry in a `SourceCitations` list. */
export function citationID({
  idPrefix,
  number,
}: {
  idPrefix: string;
  number: number;
}): string {
  return `${idPrefix}-${number}`;
}

export type CitationNumbers = {
  /** @description Each distinct citation once, in the order first seen. */
  citations: SourceCitationEntity[];
  /** @description A citation's number in `citations`, counting from 1. */
  numberOf: (citation: SourceCitationEntity) => number;
};

/**
 * @description Numbers a page's citations for footnotes: each distinct source (by
 * `citationKey`) gets the next number the first time it appears.
 * @note `numberOf` throws for a citation that was not passed in, since its mark would
 * point at nothing.
 */
export function numberCitations(
  citations: readonly SourceCitationEntity[],
): CitationNumbers {
  const numbers = new Map<string, number>();
  const distinct: SourceCitationEntity[] = [];
  for (const citation of citations) {
    const key = citationKey(citation);
    if (numbers.has(key)) continue;
    distinct.push(citation);
    numbers.set(key, distinct.length);
  }
  return {
    citations: distinct,
    numberOf: (citation) => {
      const number = numbers.get(citationKey(citation));
      if (number === undefined) {
        throw new Error(`[numberCitations] : no number for '${citation.url}'`);
      }
      return number;
    },
  };
}
