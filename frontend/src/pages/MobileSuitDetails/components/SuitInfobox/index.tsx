import type { MobileSuitDetailEntity } from '@/api';
import { VisualSlot } from '@/components';
import type { Nullable } from '@/types';

import type { Cite } from '../../utils/citations';
import type { SpecSheetEntry } from '../../utils/specSheets';
import { SheetSummary } from '../SheetSummary';
import { SuitCredits } from '../SuitCredits';

import './styles.css';

export type SuitInfoboxProps = {
  cite: Cite;
  /** @description The sheet the tabs have selected, or `null` for a suit with none. */
  selected: Nullable<SpecSheetEntry>;
  suit: MobileSuitDetailEntity;
};

/**
 * @description The dossier's side panel: the image slot, the selected spec sheet's
 * headline numbers, and who designed, built, flew and debuted the suit.
 */
export function SuitInfobox({ cite, selected, suit }: SuitInfoboxProps) {
  return (
    <aside aria-labelledby="suit-infobox-title" className="suit-infobox">
      <VisualSlot subject={suit.name} />
      <h3 className="visually-hidden" id="suit-infobox-title">
        Unit data
      </h3>
      <SheetSummary cite={cite} selected={selected} />
      <SuitCredits cite={cite} suit={suit} />
    </aside>
  );
}
