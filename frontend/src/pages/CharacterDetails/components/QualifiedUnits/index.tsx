import { useId } from 'react';

import type { PilotedMobileSuitEntity } from '@/api';
import { EntityLink, type Cite } from '@/components';

import './styles.css';

export type QualifiedUnitsProps = {
  cite: Cite;
  piloted: PilotedMobileSuitEntity[];
};

/**
 * @description The suits the character is qualified on, as a rack of cards: each with
 * its model number, the work the pairing is from when the catalog tags one, and its
 * source.
 */
export function QualifiedUnits({ cite, piloted }: QualifiedUnitsProps) {
  const headingID = useId();

  return (
    <section aria-labelledby={headingID} className="qualified-units">
      <h3 className="stencil-label" id={headingID}>
        Qualified units
      </h3>
      {piloted.length === 0 ? (
        <p className="qualified-units-none">None on file</p>
      ) : (
        <ul aria-labelledby={headingID} className="plain-list">
          {piloted.map(({ mobile_suit, source, work }) => (
            <li className="tier-node" key={`${mobile_suit.slug}-${work?.slug ?? ''}`}>
              {mobile_suit.model_number != null && (
                <span className="qualified-units-model">
                  {mobile_suit.model_number}
                </span>
              )}
              <EntityLink kind="mobileSuit" slug={mobile_suit.slug}>
                {mobile_suit.name}
              </EntityLink>
              {cite(source)}
              {work != null && (
                <span className="qualified-units-work">({work.title})</span>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
