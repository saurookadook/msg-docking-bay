import { useId } from 'react';

import type { RelatedWorkEntity } from '@/api';
import { EntityLink, type Cite } from '@/components';
import { WORK_TYPE_LABELS } from '@/constants';

import { groupRelations } from '../../utils/relations';

import './styles.css';

export type RelatedWorksProps = {
  cite: Cite;
  relations: RelatedWorkEntity[];
};

/**
 * @description The work's direct relations, grouped by type and direction, each with
 * its type, year and source.
 * @returns nothing when the catalog lists no relation
 */
export function RelatedWorks({ cite, relations }: RelatedWorksProps) {
  const headingID = useId();
  const groups = groupRelations(relations);

  if (groups.length === 0) return null;

  return (
    <section aria-labelledby={headingID} className="related-works">
      <h3 className="stencil-label" id={headingID}>
        Related works
      </h3>
      <div className="related-works-groups">
        {groups.map(({ key, label, relations: grouped }) => (
          <div className="related-works-group" key={key}>
            <h4 className="stencil-label">{label}</h4>
            <ul aria-label={label} className="plain-list">
              {grouped.map(({ source, work }) => (
                <li className="tier-node" key={work.slug}>
                  <EntityLink kind="work" slug={work.slug}>
                    {work.title}
                  </EntityLink>
                  {cite(source)}
                  <span className="related-works-meta">
                    {[WORK_TYPE_LABELS[work.work_type], work.start_date?.slice(0, 4)]
                      .filter((part) => part != null)
                      .join(' · ')}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
