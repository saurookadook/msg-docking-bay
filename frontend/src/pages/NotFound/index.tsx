import { Link, useLocation } from 'react-router';

import { DeckPanel, HazardStripe, Readout, StencilHeading } from '@/components';

import './styles.css';

/** @description The page for a path no route matches: an empty cage. */
export function NotFound() {
  const { pathname } = useLocation();

  return (
    <section aria-labelledby="not-found-title" id="not-found">
      <HazardStripe thick />
      <StencilHeading eyebrow="Error 404" id="not-found-title" level={2}>
        Cage empty
      </StencilHeading>
      <DeckPanel>
        <Readout isAmber>{`NO UNIT ASSIGNED TO ${pathname}`}</Readout>
        <p>
          Nothing is docked at this address. <Link to="/">Return to the deck</Link>.
        </p>
      </DeckPanel>
    </section>
  );
}
