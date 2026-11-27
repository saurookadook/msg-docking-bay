import { useId } from 'react';

import type { OrganizationDetailEntity, OrganizationRefEntity } from '@/api';
import { EntityLink } from '@/components';

import './styles.css';

export type OrgChartProps = {
  organization: OrganizationDetailEntity;
};

/** @description One tier of the chart above or below the organization: its linked names. */
function OrgTier({
  label,
  organizations,
}: {
  label: string;
  organizations: readonly OrganizationRefEntity[];
}) {
  if (organizations.length === 0) return null;
  return (
    <div className="org-chart-tier">
      <h4 className="stencil-label muted-label">{label}</h4>
      <ul aria-label={label} className="plain-list wrap-list">
        {organizations.map(({ name, slug }) => (
          <li className="tier-node" key={slug}>
            <EntityLink kind="organization" slug={slug}>
              {name}
            </EntityLink>
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * @description The organization's place in its hierarchy: its parent above it, and its
 * units below, as a tier tree.
 * @returns nothing when the catalog lists neither a parent nor a unit
 */
export function OrgChart({ organization }: OrgChartProps) {
  const headingID = useId();
  const { child_organizations, name, parent_organization } = organization;

  if (parent_organization == null && child_organizations.length === 0) return null;

  return (
    <section aria-labelledby={headingID} className="org-chart">
      <h3 className="stencil-label" id={headingID}>
        Org chart
      </h3>
      <div className="tier-tree">
        <OrgTier
          label="Parent"
          organizations={parent_organization == null ? [] : [parent_organization]}
        />
        <div className="org-chart-tier">
          <p aria-current="page" className="tier-node">
            {name}
          </p>
        </div>
        <OrgTier label="Units" organizations={child_organizations} />
      </div>
    </section>
  );
}
