import { NavLink } from 'react-router';

import type { EntityKind } from '@/types';
import { entityPath } from '@/utils';

import './styles.css';

export type BaySignProps = {
  kind: EntityKind;
  label: string;
  /** @description The bay's list route exists; until then its sign shows "Offline". */
  isCommissioned: boolean;
};

/** @description One hanging bay sign: a link once its bay is commissioned, else offline. */
export function BaySign({ isCommissioned, kind, label }: BaySignProps) {
  if (!isCommissioned) {
    return (
      <span className="bay-sign offline">
        {label} <span className="bay-sign-status">Offline</span>
      </span>
    );
  }

  return (
    <NavLink className="bay-sign" to={entityPath({ kind })}>
      {label}
    </NavLink>
  );
}
