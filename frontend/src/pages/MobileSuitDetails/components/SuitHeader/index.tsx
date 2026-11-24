import type { MobileSuitDetailEntity } from '@/api';
import { StencilHeading } from '@/components';
import { UNIT_TYPE_LABELS } from '@/constants';

import './styles.css';

export type SuitHeaderProps = {
  headingID: string;
  suit: MobileSuitDetailEntity;
};

/** @description The dossier's title: model number stencil, name, Japanese name and class. */
export function SuitHeader({ headingID, suit }: SuitHeaderProps) {
  const { continuity, model_number, name, name_ja, unit_type } = suit;
  return (
    <header className="suit-header">
      <StencilHeading
        eyebrow={model_number ?? 'No model number'}
        id={headingID}
        level={2}
      >
        {name}
      </StencilHeading>
      {name_ja != null && (
        <p className="suit-header-name-ja" lang="ja">
          {name_ja}
        </p>
      )}
      <p className="suit-header-class stencil-label">
        {UNIT_TYPE_LABELS[unit_type]}
        {continuity != null && ` · ${continuity.name}`}
      </p>
    </header>
  );
}
