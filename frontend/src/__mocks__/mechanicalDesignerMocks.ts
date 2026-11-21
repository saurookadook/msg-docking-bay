// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`). The cards are in `peopleMocks.ts`.
import type { DesignedMobileSuitEntity, MechanicalDesignerCardEntity } from '@/api';

import { mockMobileSuitDetails, mockMobileSuits } from './mobileSuitMocks';
import {
  mockMechanicalDesigners,
  mockMechanicalDesignerSlugRedirects,
} from './peopleMocks';

/**
 * @description Finds a designer by their current or an old slug, as
 * `GET /api/mechanical-designers/{mechanical_designer_slug}` does (D2).
 * @returns `undefined` for an unknown slug, which the route answers with a 404.
 */
export function findMechanicalDesignerMock(
  slug: string,
): MechanicalDesignerCardEntity | undefined {
  const currentSlug = mockMechanicalDesignerSlugRedirects[slug] ?? slug;
  return mockMechanicalDesigners.find((designer) => designer.slug === currentSlug);
}

/**
 * @description The suits credited to a designer, read from the suit fixtures'
 * `designers`, as `GET /api/mechanical-designers/{mechanical_designer_slug}/mobile-suits`
 * lists them: in `mockMobileSuits` order (by name).
 */
export function findMechanicalDesignerMobileSuitsMock(
  designerSlug: string,
): DesignedMobileSuitEntity[] {
  return mockMobileSuits.flatMap((card) =>
    (mockMobileSuitDetails[card.slug]?.designers ?? [])
      .filter(({ mechanical_designer }) => mechanical_designer.slug === designerSlug)
      .map(({ created_at, source }) => ({ created_at, mobile_suit: card, source })),
  );
}
