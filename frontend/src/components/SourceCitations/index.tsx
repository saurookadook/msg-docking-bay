import classNames from 'classnames';
import { useId } from 'react';

import type { SourceCitationEntity, SourceKind } from '@/api';

import './styles.css';

const SOURCE_KIND_LABELS: Record<SourceKind, string> = {
  fandom_page: 'Gundam Wiki',
  wikidata_item: 'Wikidata',
  wikipedia_en_page: 'Wikipedia (EN)',
  wikipedia_ja_page: 'Wikipedia (JA)',
};

export type SourceCitationsProps = React.HTMLAttributes<HTMLElement> & {
  citations: SourceCitationEntity[];
};

/**
 * @description Credits every source a page's facts came from, with the revision used
 * and the content licence, as CC BY-SA attribution requires.
 * @returns nothing when there are no citations
 */
export function SourceCitations({
  citations,
  className,
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
      <ul>
        {citations.map((citation) => (
          <li key={`${citation.kind}-${citation.url}`}>
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
        ))}
      </ul>
    </section>
  );
}
