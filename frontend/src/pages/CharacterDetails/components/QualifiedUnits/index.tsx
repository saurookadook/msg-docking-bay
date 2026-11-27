import type { PilotedMobileSuitEntity } from '@/api';
import { DetailSection, EntityLink, type Cite } from '@/components';

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
  return (
    <DetailSection className="qualified-units" title="Qualified units">
      {piloted.length === 0 ? (
        <p className="qualified-units-none meta-note">None on file</p>
      ) : (
        <ul aria-label="Qualified units" className="plain-list wrap-list">
          {piloted.map(({ mobile_suit, source, work }) => (
            <li className="tier-node" key={`${mobile_suit.slug}-${work?.slug ?? ''}`}>
              {mobile_suit.model_number != null && (
                <span className="meta-note">{mobile_suit.model_number}</span>
              )}
              <EntityLink kind="mobileSuit" slug={mobile_suit.slug}>
                {mobile_suit.name}
              </EntityLink>
              {cite(source)}
              {work != null && <span className="meta-note">({work.title})</span>}
            </li>
          ))}
        </ul>
      )}
    </DetailSection>
  );
}
