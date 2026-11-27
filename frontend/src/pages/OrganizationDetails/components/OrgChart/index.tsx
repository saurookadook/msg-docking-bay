import { useId } from 'react';

import type { OrganizationDetailEntity } from '@/api';
import { EntityLink } from '@/components';

import './styles.css';

export type OrgChartProps = {
  organization: OrganizationDetailEntity;
};

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
        {parent_organization != null && (
          <div className="org-chart-tier">
            <h4 className="stencil-label muted-label">Parent</h4>
            <ul aria-label="Parent" className="plain-list wrap-list">
              <li className="tier-node">
                <EntityLink kind="organization" slug={parent_organization.slug}>
                  {parent_organization.name}
                </EntityLink>
              </li>
            </ul>
          </div>
        )}
        <div className="org-chart-tier">
          <p aria-current="page" className="tier-node">
            {name}
          </p>
        </div>
        {child_organizations.length > 0 && (
          <div className="org-chart-tier">
            <h4 className="stencil-label muted-label">Units</h4>
            <ul aria-label="Units" className="plain-list wrap-list">
              {child_organizations.map((child) => (
                <li className="tier-node" key={child.slug}>
                  <EntityLink kind="organization" slug={child.slug}>
                    {child.name}
                  </EntityLink>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
