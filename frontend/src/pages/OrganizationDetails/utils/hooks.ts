import type { OrganizationMobileSuitEntity } from '@/api';
import { useCatalogSubList, type ListState } from '@/store';

import type { RoleSection } from './roleSections';

/**
 * @description One role section's page of suits, loaded once the organization is.
 * @note `slug` is the organization's current slug, from its loaded detail.
 */
export function useRoleSection({
  section,
  slug,
}: {
  section: RoleSection;
  slug: string;
}): ListState<OrganizationMobileSuitEntity> {
  return useCatalogSubList({
    apiQuery: section.apiQuery,
    fetchSubList: section.fetchSubList,
    selectList: section.selectList,
    slug,
  });
}
