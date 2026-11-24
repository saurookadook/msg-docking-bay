import { useId } from 'react';

import type { WorkAppearanceEntity } from '@/api';
import { EntityLink, StatusLamp } from '@/components';
import { WORK_TYPE_LABELS } from '@/constants';

import type { Cite } from '../../utils/citations';
import { formatEpisodes } from '../../utils/format';

import './styles.css';

export type SuitAppearancesProps = {
  appearances: WorkAppearanceEntity[];
  cite: Cite;
};

/**
 * @description The works the suit appears in, in the API's order (by start date), with
 * its debut marked and the episodes it is in.
 * @returns nothing when the catalog lists no appearance
 */
export function SuitAppearances({ appearances, cite }: SuitAppearancesProps) {
  const headingID = useId();

  if (appearances.length === 0) return null;

  return (
    <section aria-labelledby={headingID} className="suit-appearances">
      <h3 className="stencil-label" id={headingID}>
        Appearances
      </h3>
      <ul>
        {appearances.map(({ first_episode, is_debut, last_episode, source, work }) => {
          const episodes = formatEpisodes({ first_episode, last_episode });
          const year = work.start_date?.slice(0, 4);
          return (
            <li key={work.slug}>
              <EntityLink kind="work" slug={work.slug}>
                {work.title}
              </EntityLink>
              {cite(source)}
              <span className="suit-appearances-meta">
                {[WORK_TYPE_LABELS[work.work_type], year, episodes]
                  .filter((part) => part != null)
                  .join(' · ')}
              </span>
              {is_debut && <StatusLamp status="online">Debut</StatusLamp>}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
