import { useId } from 'react';

import type { SourceCitationEntity, WorkCardEntity } from '@/api';
import { EntityLink, StatusLamp, type Cite } from '@/components';
import { WORK_TYPE_LABELS } from '@/constants';
import type { Nullable } from '@/types';
import { formatEpisodes, joinParts, yearOf } from '@/utils';

import './styles.css';

/**
 * @description One work an entity appears in, cited to its source. A suit's appearances
 * also carry their episodes and debut; a character's or organization's do not.
 */
export type WorkAppearanceItem = {
  first_episode?: Nullable<number>;
  is_debut?: boolean;
  last_episode?: Nullable<number>;
  source: SourceCitationEntity;
  work: WorkCardEntity;
};

export type WorkAppearancesProps = {
  appearances: readonly WorkAppearanceItem[];
  cite: Cite;
};

/**
 * @description The works an entity appears in, in the API's order (by start date), each
 * with its type and year, its episodes and its debut when known.
 * @returns nothing when the catalog lists no appearance
 */
export function WorkAppearances({ appearances, cite }: WorkAppearancesProps) {
  const headingID = useId();

  if (appearances.length === 0) return null;

  return (
    <section aria-labelledby={headingID} className="work-appearances">
      <h3 className="stencil-label" id={headingID}>
        Appearances
      </h3>
      <ul className="plain-list">
        {appearances.map(
          ({
            first_episode = null,
            is_debut = false,
            last_episode = null,
            source,
            work,
          }) => {
            const episodes = formatEpisodes({ first_episode, last_episode });
            return (
              <li key={work.slug}>
                <EntityLink kind="work" slug={work.slug}>
                  {work.title}
                </EntityLink>
                {cite(source)}
                <span className="work-appearances-meta">
                  {joinParts([
                    WORK_TYPE_LABELS[work.work_type],
                    yearOf(work.start_date),
                    episodes,
                  ])}
                </span>
                {is_debut && <StatusLamp status="online">Debut</StatusLamp>}
              </li>
            );
          },
        )}
      </ul>
    </section>
  );
}
