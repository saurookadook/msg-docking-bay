import { Link } from 'react-router';

import { DeckPanel, Readout, StencilHeading } from '@/components';

import './styles.css';

export function Home() {
  return (
    <section aria-labelledby="home-title" id="home">
      <StencilHeading eyebrow="MS DECK 01" id="home-title" level={2}>
        Welcome aboard
      </StencilHeading>
      <DeckPanel>
        <Readout typesOn>MS DECK 01 · STANDING BY</Readout>
        <p>
          MSG Docking Bay is under construction: its bays come online one by one as the
          catalog's pages land.
        </p>
        <p>
          Check that the API is reachable on the{' '}
          <Link to="/health-check">health check page</Link>.
        </p>
      </DeckPanel>
    </section>
  );
}
