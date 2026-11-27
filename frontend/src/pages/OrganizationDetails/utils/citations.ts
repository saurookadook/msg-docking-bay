import type {
  OrganizationDetailEntity,
  OrganizationMobileSuitEntity,
  SourceCitationEntity,
} from '@/api';

/** @description The `idPrefix` linking the faction registry's marks to its source list. */
export const SOURCE_ID_PREFIX = 'organization-source';

/**
 * @description Every source the faction registry cites, in the order a reader meets
 * them: the appearances, then each role section's links on its current page.
 * @note Duplicates stay; `numberCitations` numbers each distinct source once.
 */
export function collectCitations({
  organization,
  sections,
}: {
  organization: OrganizationDetailEntity;
  sections: readonly (readonly OrganizationMobileSuitEntity[])[];
}): SourceCitationEntity[] {
  return [
    ...organization.appearances.map(({ source }) => source),
    ...sections.flat().flatMap(({ links }) => links.map(({ source }) => source)),
  ];
}
