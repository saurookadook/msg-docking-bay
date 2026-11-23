import type { EntityKind } from '@/types';

export type BaySign = {
  label: string;
  kind: EntityKind;
  /** @description The bay's list route exists; until then its sign shows "Offline". */
  isCommissioned: boolean;
};

/**
 * @description The nav's hanging bay signs, in deck order.
 * @note F2 to F4 commission each bay as its list page lands.
 */
export const BAY_SIGNS: BaySign[] = [
  { label: 'Mobile Suits', kind: 'mobileSuit', isCommissioned: false },
  { label: 'Personnel', kind: 'character', isCommissioned: false },
  { label: 'Organizations', kind: 'organization', isCommissioned: false },
  { label: 'Works', kind: 'work', isCommissioned: false },
  { label: 'Designers', kind: 'mechanicalDesigner', isCommissioned: false },
];
