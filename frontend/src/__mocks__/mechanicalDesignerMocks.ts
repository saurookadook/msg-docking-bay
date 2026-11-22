// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`). The cards are in `peopleMocks.ts`.
import type { DesignedMobileSuitEntity, MechanicalDesignerDetailEntity } from '@/api';

import { creditsBySuit } from './mobileSuitMocks';
import {
  findBySlugOrRedirect,
  mockMechanicalDesigners,
  mockMechanicalDesignerSlugRedirects,
} from './peopleMocks';

/**
 * @description Each designer's detail, keyed by their current slug. A detail holds only
 * the card's fields: their suits are a route of their own (Q1).
 */
export const mockMechanicalDesignerDetails: Readonly<
  Record<string, MechanicalDesignerDetailEntity>
> = Object.fromEntries(mockMechanicalDesigners.map((card) => [card.slug, { ...card }]));

/**
 * @description Finds a designer's detail by their current or an old slug, as
 * `GET /api/mechanical-designers/{mechanical_designer_slug}` does (D2).
 * @returns `undefined` for an unknown slug, which the route answers with a 404.
 */
export function findMechanicalDesignerMock(
  slug: string,
): MechanicalDesignerDetailEntity | undefined {
  return findBySlugOrRedirect({
    byCurrentSlug: mockMechanicalDesignerDetails,
    redirects: mockMechanicalDesignerSlugRedirects,
    slug,
  });
}

/**
 * @description The suits credited to a designer, read from the suit fixtures'
 * `designers`, as `GET /api/mechanical-designers/{mechanical_designer_slug}/mobile-suits`
 * lists them: in `mockMobileSuits` order (by name).
 */
export function findMechanicalDesignerMobileSuitsMock(
  designerSlug: string,
): DesignedMobileSuitEntity[] {
  return creditsBySuit({
    credits: ({ designers }) => designers,
    matches: ({ mechanical_designer }) => mechanical_designer.slug === designerSlug,
  }).flatMap(({ card, credits }) =>
    credits.map(({ created_at, source }) => ({
      created_at,
      mobile_suit: card,
      source,
    })),
  );
}
