import classNames from 'classnames';
import { Link, type LinkProps } from 'react-router';

import type { EntityKind } from '@/types';
import { entityPath } from '@/utils';

import './styles.css';

// NOTE: original line icons, one per kind, drawn on a 16-unit grid.
const ENTITY_ICON_PATHS: Record<EntityKind, string> = {
  // A visored head.
  mobileSuit: 'M5 2h6l2 4v5l-2 3H5l-2-3V6zM5 7h6',
  // A pilot's helmet and shoulders.
  character: 'M8 2a3 3 0 1 1 0 6a3 3 0 1 1 0-6zM2 14c1-3 3-4 6-4s5 1 6 4',
  // A faction shield.
  organization: 'M8 1l6 2v5c0 3-3 6-6 7c-3-1-6-4-6-7V3z',
  // An operation log's film strip.
  work: 'M2 3h12v10H2zM5 3v10M11 3v10M2 8h3M11 8h3',
  // A drafting compass.
  mechanicalDesigner: 'M8 1v3M8 4l-5 11M8 4l5 11M5 10h6',
};

export type EntityLinkProps = Omit<LinkProps, 'to'> & {
  kind: EntityKind;
  slug: string;
};

/** @description A link to an entity's page, marked with its kind's icon. */
export function EntityLink({
  children,
  className,
  kind,
  slug,
  ...props
}: EntityLinkProps) {
  return (
    <Link
      className={classNames('entity-link', className)}
      to={entityPath({ kind, slug })}
      {...props}
    >
      <svg aria-hidden="true" className="entity-link-icon" viewBox="0 0 16 16">
        <path d={ENTITY_ICON_PATHS[kind]} />
      </svg>
      {children}
    </Link>
  );
}
