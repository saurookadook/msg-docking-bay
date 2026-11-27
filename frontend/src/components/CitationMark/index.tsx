import classNames from 'classnames';

import type { SourceCitationEntity } from '@/api';
import { citationID } from '@/utils';

import './styles.css';

export type CitationMarkProps = React.HTMLAttributes<HTMLElement> & {
  /** @description The `idPrefix` of the page's `SourceCitations`. */
  idPrefix: string;
  /** @description The source's number in that list (`numberCitations`). */
  number: number;
};

/** @description Renders the footnote mark for a fact's source: a `CitationMark` with its number. */
export type Cite = (source: SourceCitationEntity) => React.ReactElement;

/** @description A footnote mark, `[n]`, linking a fact to its source's entry. */
export function CitationMark({
  className,
  idPrefix,
  number,
  ...props
}: CitationMarkProps) {
  return (
    <sup className={classNames('citation-mark', className)} {...props}>
      <a aria-label={`Source ${number}`} href={`#${citationID({ idPrefix, number })}`}>
        [{number}]
      </a>
    </sup>
  );
}
