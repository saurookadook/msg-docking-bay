import type { MobileSuitOrganizationRole, OrganizationMobileSuitEntity } from '@/api';
import { fetchOrganizationMobileSuits, type AppState, type ListState } from '@/store';
import type { BaseAction } from '@/store/types';

/** @description One role section of the faction registry's mobile weapons. */
export type RoleSection = {
  /** @description The API query for the section's page, with its `role`. */
  apiQuery: (searchParams: URLSearchParams) => string;
  fetchSubList: (args: BaseAction & { query: string; slug: string }) => Promise<void>;
  /** @description The search param the section's pager writes. */
  offsetParam: string;
  role: MobileSuitOrganizationRole;
  selectList: (appState: AppState) => ListState<OrganizationMobileSuitEntity>;
  title: string;
};

/**
 * @description The API query for one role section: its `role`, the page's `limit`, and
 * the section's own offset param as `offset`, sorted by key.
 * @example
 * ```ts
 * roleSectionQuery({ offsetParam: 'operator_offset', role: 'operator' })(
 *   new URLSearchParams('operator_offset=50&offset=4'),
 * ); // 'offset=50&role=operator'
 * ```
 */
export function roleSectionQuery({
  offsetParam,
  role,
}: {
  offsetParam: string;
  role: MobileSuitOrganizationRole;
}): (searchParams: URLSearchParams) => string {
  return (searchParams) => {
    const apiParams = new URLSearchParams();
    const limit = searchParams.get('limit')?.trim() ?? '';
    const offset = searchParams.get(offsetParam)?.trim() ?? '';
    if (limit !== '') apiParams.set('limit', limit);
    if (offset !== '') apiParams.set('offset', offset);
    apiParams.set('role', role);
    return apiParams.toString();
  };
}

function roleSection({
  role,
  title,
}: {
  role: MobileSuitOrganizationRole;
  title: string;
}): RoleSection {
  const offsetParam = `${role}_offset`;
  return {
    apiQuery: roleSectionQuery({ offsetParam, role }),
    fetchSubList: (args) => fetchOrganizationMobileSuits({ ...args, role }),
    offsetParam,
    role,
    selectList: (appState) => appState.organizations.mobileSuitsByRole[role],
    title,
  };
}

// NOTE: module-level, so each section's fetch and query stay stable across renders.
export const MANUFACTURED = roleSection({
  role: 'manufacturer',
  title: 'Manufactured',
});
export const OPERATED = roleSection({ role: 'operator', title: 'Operated' });
export const DEVELOPED = roleSection({ role: 'developer', title: 'Developed' });
