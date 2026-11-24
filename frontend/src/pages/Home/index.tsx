import { Link } from 'react-router';

import { DeckPanel, Readout, StencilHeading } from '@/components';
import { ENTITY_KINDS } from '@/constants';
import type { EntityKind } from '@/types';
import { entityPath } from '@/utils';

import './styles.css';

// NOTE: `Object.keys` types its result as string[]; these are ENTITY_KINDS' own keys.
const BAY_KINDS = Object.keys(ENTITY_KINDS) as EntityKind[];

export function Home() {
  const commissionedKinds = BAY_KINDS.filter(
    (kind) => ENTITY_KINDS[kind].isCommissioned,
  );

  return (
    <section aria-labelledby="home-title" id="home">
      <StencilHeading eyebrow="MS DECK 01" id="home-title" level={2}>
        Welcome aboard
      </StencilHeading>
      <DeckPanel>
        <Readout isTypingOn>MS DECK 01 · STANDING BY</Readout>
        <p>Pick a bay to browse its roster.</p>
        <nav aria-label="Bay directory">
          <ul className="home-bay-directory">
            {commissionedKinds.map((kind) => (
              <li key={kind}>
                <Link to={entityPath({ kind })}>{ENTITY_KINDS[kind].navLabel}</Link>
              </li>
            ))}
          </ul>
        </nav>
        <p>
          Check that the API is reachable on the{' '}
          <Link to="/health-check">health check page</Link>.
        </p>
      </DeckPanel>
    </section>
  );
}
