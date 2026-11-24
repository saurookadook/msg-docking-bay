import classNames from 'classnames';

import { citationID } from '@/components/SourceCitations/citationNumbers';

import './styles.css';

export type CitationMarkProps = React.HTMLAttributes<HTMLElement> & {
  /** @description The `idPrefix` of the page's `SourceCitations`. */
  idPrefix: string;
  /** @description The source's number in that list (`numberCitations`). */
  number: number;
};

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
