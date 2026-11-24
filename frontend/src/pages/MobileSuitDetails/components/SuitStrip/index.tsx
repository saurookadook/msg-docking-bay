import type { MobileSuitDetailEntity } from '@/api';
import { VisualSlot } from '@/components';

import { ModelNumber } from '../ModelNumber';

import './styles.css';

export type SuitStripProps = {
  suit: MobileSuitDetailEntity;
};

/**
 * @description The phone-width strip pinned at the top of the dossier, keeping the
 * suit's image and name in view while the infobox scrolls away.
 * @note Hidden from assistive tech: it repeats the header.
 */
export function SuitStrip({ suit }: SuitStripProps) {
  return (
    <div aria-hidden="true" className="suit-strip">
      <VisualSlot className="suit-strip-visual" subject={suit.name} />
      <p className="stencil-label">
        <ModelNumber className="suit-strip-model" modelNumber={suit.model_number} />
        {suit.name}
      </p>
    </div>
  );
}
