// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`). The cards are in `peopleMocks.ts`.
import type {
  CitedWorkEntity,
  OrganizationCardEntity,
  OrganizationDetailEntity,
  OrganizationMobileSuitEntity,
} from '@/api';

import { mockSources } from './catalogMocks';
import { citedWork } from './characterMocks';
import { mockMobileSuitDetails, mockMobileSuits } from './mobileSuitMocks';
import {
  mockEarthFederation,
  mockOrganizationSlugRedirects,
  mockPrincipalityOfZeon,
  mockZeonic,
} from './peopleMocks';
import { mockMobileSuitGundam, mockMobileSuitGundamI } from './workMocks';

// None of the seeded organizations has a parent or a unit.
function detail(
  card: OrganizationCardEntity,
  appearances: CitedWorkEntity[],
): OrganizationDetailEntity {
  return { ...card, appearances, child_organizations: [] };
}

/** @description Each organization's detail, keyed by its current slug. */
export const mockOrganizationDetails: Readonly<
  Record<string, OrganizationDetailEntity>
> = {
  [mockEarthFederation.slug]: detail(mockEarthFederation, [
    citedWork(mockMobileSuitGundam, mockSources.earthFederation),
    citedWork(mockMobileSuitGundamI, mockSources.earthFederation),
  ]),
  [mockPrincipalityOfZeon.slug]: detail(mockPrincipalityOfZeon, [
    citedWork(mockMobileSuitGundam, mockSources.principalityOfZeon),
    citedWork(mockMobileSuitGundamI, mockSources.principalityOfZeon),
  ]),
  // Its page lists no seeded work.
  [mockZeonic.slug]: detail(mockZeonic, []),
};

/**
 * @description Finds an organization's detail by its current or an old slug, as
 * `GET /api/organizations/{organization_slug}` does (D2).
 * @returns `undefined` for an unknown slug, which the route answers with a 404.
 */
export function findOrganizationMock(
  slug: string,
): OrganizationDetailEntity | undefined {
  return (
    mockOrganizationDetails[slug] ??
    mockOrganizationDetails[mockOrganizationSlugRedirects[slug] ?? '']
  );
}

/**
 * @description An organization's suits, as
 * `GET /api/organizations/{organization_slug}/mobile-suits` lists them: one item per
 * suit, in `mockMobileSuits` order (by name), with its links in the suit fixture's order.
 * @note `role` is not applied: Mirage filters are opt-in (D7).
 */
export function findOrganizationMobileSuitsMock(
  organizationSlug: string,
): OrganizationMobileSuitEntity[] {
  return mockMobileSuits.flatMap((card) => {
    const links = (mockMobileSuitDetails[card.slug]?.organizations ?? [])
      .filter(({ organization }) => organization.slug === organizationSlug)
      .map(({ created_at, role, source, work }) => ({
        created_at,
        role,
        source,
        work,
      }));
    return links.length === 0 ? [] : [{ links, mobile_suit: card }];
  });
}
