import { useId } from 'react';

import { DeckPanel } from '@/components';

import './styles.css';

/** @description An empty slot reading "DATA PENDING", for a part the catalog lacks. */
export function PendingPanel() {
  return (
    <DeckPanel className="pending-panel">
      <p className="stencil-label">DATA PENDING</p>
    </DeckPanel>
  );
}

/** @description A wiki section the catalog does not hold yet: its heading over a `PendingPanel`. */
export function PendingSection({ title }: { title: string }) {
  const headingID = useId();
  return (
    <section aria-labelledby={headingID} className="pending-section">
      <h3 className="stencil-label" id={headingID}>
        {title}
      </h3>
      <PendingPanel />
    </section>
  );
}
