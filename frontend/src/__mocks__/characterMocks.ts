// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`). The cards are in `peopleMocks.ts`.
import type {
  CharacterCardEntity,
  CharacterDetailEntity,
  CitedWorkEntity,
  PilotedMobileSuitEntity,
  SourceCitationEntity,
  WorkCardEntity,
} from '@/api';

import { mockNow, mockSources } from './catalogMocks';
import { creditsBySuit } from './mobileSuitMocks';
import {
  findBySlugOrRedirect,
  mockAmuroRay,
  mockAmuroRayOrigin,
  mockCharacterSlugRedirects,
} from './peopleMocks';
import {
  mockMobileSuitGundam,
  mockMobileSuitGundamI,
  mockTheOrigin,
  mockWorks,
} from './workMocks';

/** @description A work the page's `series` list names, cited to that page. */
export function createCitedWorkMock({
  source,
  work,
}: {
  source: SourceCitationEntity;
  work: WorkCardEntity;
}): CitedWorkEntity {
  return { created_at: mockNow, source, work };
}

/** @description Where a work falls in release order; a pairing with no work goes last. */
function releaseRank(workSlug: string | undefined): number {
  const index = mockWorks.findIndex(({ slug }) => slug === workSlug);
  return index === -1 ? mockWorks.length : index;
}

/**
 * @description The suits a character pilots, read from the suit fixtures' `pilots`, in
 * the API's order: by work's release (none last), then in `mockMobileSuits` order.
 */
function pilotedMobileSuits(characterSlug: string): PilotedMobileSuitEntity[] {
  const piloted = creditsBySuit({
    credits: ({ pilots }) => pilots,
    matches: ({ character }) => character.slug === characterSlug,
  }).flatMap(({ card, credits }) =>
    credits.map(({ created_at, source, work }) => ({
      created_at,
      mobile_suit: card,
      source,
      work,
    })),
  );
  return piloted.toSorted(
    (a, b) => releaseRank(a.work?.slug) - releaseRank(b.work?.slug),
  );
}

function createCharacterDetailMock({
  appearances,
  card,
}: {
  appearances: CitedWorkEntity[];
  card: CharacterCardEntity;
}): CharacterDetailEntity {
  return { ...card, appearances, piloted_mobile_suits: pilotedMobileSuits(card.slug) };
}

/** @description Each character's detail, keyed by their current slug. */
export const mockCharacterDetails: Readonly<Record<string, CharacterDetailEntity>> = {
  [mockAmuroRay.slug]: createCharacterDetailMock({
    appearances: [
      createCitedWorkMock({ source: mockSources.amuroRay, work: mockMobileSuitGundam }),
      createCitedWorkMock({
        source: mockSources.amuroRay,
        work: mockMobileSuitGundamI,
      }),
    ],
    card: mockAmuroRay,
  }),
  [mockAmuroRayOrigin.slug]: createCharacterDetailMock({
    appearances: [
      createCitedWorkMock({ source: mockSources.amuroRayOrigin, work: mockTheOrigin }),
    ],
    card: mockAmuroRayOrigin,
  }),
};

/**
 * @description Finds a character's detail by their current or an old slug, as
 * `GET /api/characters/{character_slug}` does (D2).
 * @returns `undefined` for an unknown slug, which the route answers with a 404.
 */
export function findCharacterMock(slug: string): CharacterDetailEntity | undefined {
  return findBySlugOrRedirect({
    byCurrentSlug: mockCharacterDetails,
    redirects: mockCharacterSlugRedirects,
    slug,
  });
}
