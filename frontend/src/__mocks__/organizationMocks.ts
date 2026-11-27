// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`). The cards are in `peopleMocks.ts`.
import type {
  CitedWorkEntity,
  MobileSuitOrganizationRole,
  OrganizationCardEntity,
  OrganizationDetailEntity,
  OrganizationMobileSuitEntity,
  ValidationError,
} from '@/api';
import { ORGANIZATION_ROLE_LABELS } from '@/constants';

import { mockSources } from './catalogMocks';
import { createCitedWorkMock } from './characterMocks';
import { enumMessage } from './listFilters';
import { creditsBySuit } from './mobileSuitMocks';
import {
  findBySlugOrRedirect,
  mockEarthFederation,
  mockOrganizationSlugRedirects,
  mockPrincipalityOfZeon,
  mockZeonic,
} from './peopleMocks';
import { mockMobileSuitGundam, mockMobileSuitGundamI } from './workMocks';

// NOTE: none of the seeded organizations has a parent or a unit.
function createOrganizationDetailMock({
  appearances,
  card,
}: {
  appearances: CitedWorkEntity[];
  card: OrganizationCardEntity;
}): OrganizationDetailEntity {
  return { ...card, appearances, child_organizations: [] };
}

/** @description Each organization's detail, keyed by its current slug. */
export const mockOrganizationDetails: Readonly<
  Record<string, OrganizationDetailEntity>
> = {
  [mockEarthFederation.slug]: createOrganizationDetailMock({
    appearances: [
      createCitedWorkMock({
        source: mockSources.earthFederation,
        work: mockMobileSuitGundam,
      }),
      createCitedWorkMock({
        source: mockSources.earthFederation,
        work: mockMobileSuitGundamI,
      }),
    ],
    card: mockEarthFederation,
  }),
  [mockPrincipalityOfZeon.slug]: createOrganizationDetailMock({
    appearances: [
      createCitedWorkMock({
        source: mockSources.principalityOfZeon,
        work: mockMobileSuitGundam,
      }),
      createCitedWorkMock({
        source: mockSources.principalityOfZeon,
        work: mockMobileSuitGundamI,
      }),
    ],
    card: mockPrincipalityOfZeon,
  }),
  // NOTE: its page lists no seeded work.
  [mockZeonic.slug]: createOrganizationDetailMock({
    appearances: [],
    card: mockZeonic,
  }),
};

/**
 * @description Finds an organization's detail by its current or an old slug, as
 * `GET /api/organizations/{organization_slug}` does (D2).
 * @returns `undefined` for an unknown slug, which the route answers with a 404.
 */
export function findOrganizationMock(
  slug: string,
): OrganizationDetailEntity | undefined {
  return findBySlugOrRedirect({
    byCurrentSlug: mockOrganizationDetails,
    redirects: mockOrganizationSlugRedirects,
    slug,
  });
}

/**
 * @description An organization's suits, as
 * `GET /api/organizations/{organization_slug}/mobile-suits` lists them: one item per
 * suit, in `mockMobileSuits` order (by name), with its links in the suit fixture's order.
 * A `role` keeps only the suits with that role, and only those links, as the API does.
 */
export function findOrganizationMobileSuitsMock({
  organizationSlug,
  role,
}: {
  organizationSlug: string;
  role?: MobileSuitOrganizationRole;
}): OrganizationMobileSuitEntity[] {
  return creditsBySuit({
    credits: ({ organizations }) => organizations,
    matches: (credit) =>
      credit.organization.slug === organizationSlug &&
      (role == null || credit.role === role),
  }).map(({ card, credits }) => ({
    links: credits.map(({ created_at, role, source, work }) => ({
      created_at,
      role,
      source,
      work,
    })),
    mobile_suit: card,
  }));
}

/** @description Whether a query value is a role an organization's suit list takes. */
function isOrganizationRole(value: unknown): value is MobileSuitOrganizationRole {
  return typeof value === 'string' && Object.hasOwn(ORGANIZATION_ROLE_LABELS, value);
}

/**
 * @description An organization's suits for the route's `role` query value, or FastAPI's
 * error for a role it doesn't know.
 * @note `slug` is the organization's current slug: the route resolves it first.
 */
export function findOrganizationMobileSuitsForQueryMock({
  role,
  slug,
}: {
  role: unknown;
  slug: string;
}): OrganizationMobileSuitEntity[] | ValidationError {
  if (role == null) return findOrganizationMobileSuitsMock({ organizationSlug: slug });
  if (isOrganizationRole(role)) {
    return findOrganizationMobileSuitsMock({ organizationSlug: slug, role });
  }
  return {
    loc: ['query', 'role'],
    msg: enumMessage(Object.keys(ORGANIZATION_ROLE_LABELS)),
    type: 'enum',
  };
}
