import { NavLink } from 'react-router';

import { entityPath } from '@/utils';

import type { BaySign as BaySignConfig } from '../../baySigns';

/** @description One hanging bay sign: a link once its bay is commissioned, else offline. */
export function BaySign({ isCommissioned, kind, label }: BaySignConfig) {
  if (!isCommissioned) {
    return (
      <span aria-disabled="true" className="bay-sign offline">
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
