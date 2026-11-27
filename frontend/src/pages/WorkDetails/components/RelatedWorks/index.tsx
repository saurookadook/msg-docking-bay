import type { RelatedWorkEntity } from '@/api';
import { DetailSection, EntityLink, type Cite } from '@/components';
import { WORK_TYPE_LABELS } from '@/constants';
import { joinParts, yearOf } from '@/utils';

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
  const groups = groupRelations(relations);

  if (groups.length === 0) return null;

  return (
    <DetailSection className="related-works" title="Related works">
      <div className="related-works-groups">
        {groups.map(({ key, label, relations: grouped }) => (
          <div className="related-works-group" key={key}>
            <h4 className="stencil-label muted-label">{label}</h4>
            <ul aria-label={label} className="plain-list wrap-list">
              {grouped.map(({ source, work }) => (
                <li className="tier-node" key={work.slug}>
                  <EntityLink kind="work" slug={work.slug}>
                    {work.title}
                  </EntityLink>
                  {cite(source)}
                  <span className="meta-note">
                    {joinParts([
                      WORK_TYPE_LABELS[work.work_type],
                      yearOf(work.start_date),
                    ])}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </DetailSection>
  );
}
