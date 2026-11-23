// Shared values for the catalog fixtures (D7 in `docs/plans/catalog-read-api.md`).
//
// Every catalog fixture is read by hand from the Gundam Wiki dump of 2026-11-15
// (`gundam_pages_current.xml.7z`), the same values as `backend/scripts/seed_dev.py`.
// The seed is the other copy: change both together.
import type { ContinuityRefEntity, SourceCitationEntity } from '@/api';

/** @description The one `created_at` and `updated_at` every catalog fixture shares (TEST-20). */
export const mockNow = '2026-11-21T00:00:00Z';

/** @description The dump's `Last-Modified`: when these copies of the pages were made. */
export const mockRetrievedAt = '2026-11-15T23:32:58Z';

export const mockUniversalCenturyRef: ContinuityRefEntity = {
  name: 'Universal Century',
  slug: 'universal-century',
};

function fandomCitation(url: string, revisionId: number): SourceCitationEntity {
  return {
    content_license: 'cc_by_sa_3_0',
    kind: 'fandom_page',
    license_name: 'CC BY-SA 3.0',
    license_url: 'https://creativecommons.org/licenses/by-sa/3.0/',
    retrieved_at: mockRetrievedAt,
    revision_id: revisionId,
    revision_url: `${url}?oldid=${revisionId}`,
    url,
  };
}

const WIKI = 'https://gundam.fandom.com/wiki';

/** @description Each seeded page's citation, at the revision the dump holds. */
export const mockSources = {
  amuroRay: fandomCitation(`${WIKI}/Amuro_Ray`, 705278),
  amuroRayOrigin: fandomCitation(`${WIKI}/Amuro_Ray_(Origin)`, 694015),
  earthFederation: fandomCitation(`${WIKI}/Earth_Federation`, 685169),
  itMoves: fandomCitation(`${WIKI}/It_Moves%3F_Gundam,_Follow_Your_Dreams!`, 637504),
  mobileSuitGundam: fandomCitation(`${WIKI}/Mobile_Suit_Gundam`, 665644),
  mobileSuitGundamI: fandomCitation(`${WIKI}/Mobile_Suit_Gundam_I`, 703163),
  principalityOfZeon: fandomCitation(`${WIKI}/Principality_of_Zeon`, 701574),
  ms06fZakuII: fandomCitation(`${WIKI}/MS-06F_Zaku_II`, 706593),
  rx7802Gundam: fandomCitation(`${WIKI}/RX-78-02_Gundam`, 707929),
  rx782Gundam: fandomCitation(`${WIKI}/RX-78-2_Gundam`, 707889),
  rx78f00Gundam: fandomCitation(`${WIKI}/RX-78F00_Gundam`, 707440),
  theOrigin: fandomCitation(`${WIKI}/Mobile_Suit_Gundam:_The_Origin`, 705008),
  theOriginAdvent: fandomCitation(
    `${WIKI}/Mobile_Suit_Gundam:_The_Origin_Advent_of_the_Red_Comet`,
    693655,
  ),
} satisfies Record<string, SourceCitationEntity>;

/**
 * @description A Wikidata citation, which has no revision link and a CC0 licence.
 * @note Not in the seed: no fixture entity cites Wikidata yet. Components that render
 * citations use it to cover the non-wiki kinds.
 */
export const mockWikidataSource: SourceCitationEntity = {
  content_license: 'cc0_1_0',
  kind: 'wikidata_item',
  license_name: 'CC0 1.0',
  license_url: 'https://creativecommons.org/publicdomain/zero/1.0/',
  retrieved_at: mockRetrievedAt,
  revision_id: null,
  revision_url: null,
  url: 'https://www.wikidata.org/wiki/Q1',
};
