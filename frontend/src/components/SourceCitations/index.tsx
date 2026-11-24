import classNames from 'classnames';
import { useId } from 'react';

import type { SourceCitationEntity } from '@/api';
import { SOURCE_KIND_LABELS } from '@/constants';
import { citationID, citationKey } from '@/utils';

import './styles.css';

export type SourceCitationsProps = React.HTMLAttributes<HTMLElement> & {
  /** @description Distinct citations, in footnote order (`numberCitations`). */
  citations: SourceCitationEntity[];
  /**
   * @description Gives each entry the `id` a `CitationMark` with the same prefix links
   * to. Without it, the entries have no `id`.
   */
  idPrefix?: string;
};

/**
 * @description Credits every source a page's facts came from, numbered, with the
 * revision used and the content licence, as CC BY-SA attribution requires.
 * @returns nothing when there are no citations
 */
export function SourceCitations({
  citations,
  className,
  idPrefix,
  ...props
}: SourceCitationsProps) {
  const headingID = useId();

  if (citations.length === 0) return null;

  return (
    <section
      aria-labelledby={headingID}
      className={classNames('source-citations', className)}
      {...props}
    >
      <h3 className="stencil-label" id={headingID}>
        Sources
      </h3>
      <ol>
        {citations.map((citation, index) => {
          const number = index + 1;
          return (
            <li
              id={idPrefix == null ? undefined : citationID({ idPrefix, number })}
              key={citationKey(citation)}
            >
              <span aria-hidden="true" className="source-citations-number">
                [{number}]
              </span>
              <a href={citation.url} rel="external noreferrer">
                {SOURCE_KIND_LABELS[citation.kind]}
              </a>
              {citation.revision_url != null && (
                <a href={citation.revision_url} rel="external noreferrer">
                  revision{citation.revision_id != null && ` ${citation.revision_id}`}
                </a>
              )}
              <a href={citation.license_url} rel="license external noreferrer">
                {citation.license_name}
              </a>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
