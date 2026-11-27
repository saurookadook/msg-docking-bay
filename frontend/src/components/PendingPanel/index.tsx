import { DeckPanel, DetailSection } from '@/components';

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
  return (
    <DetailSection className="pending-section" title={title}>
      <PendingPanel />
    </DetailSection>
  );
}
