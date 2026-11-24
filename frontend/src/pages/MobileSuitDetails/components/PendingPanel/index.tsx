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
