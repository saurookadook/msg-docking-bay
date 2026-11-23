import classNames from 'classnames';
import { Link, type LinkProps } from 'react-router';

import { ENTITY_KINDS } from '@/constants';
import type { EntityKind } from '@/types';
import { entityPath } from '@/utils';

import './styles.css';

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
        <path d={ENTITY_KINDS[kind].iconPath} />
      </svg>
      {children}
    </Link>
  );
}
