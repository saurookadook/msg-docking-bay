// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`).
import type { RelatedWorkEntity, WorkCardEntity, WorkDetailEntity } from '@/api';

import { mockNow, mockSources, mockUniversalCenturyRef } from './catalogMocks';

const timestamps = { created_at: mockNow, updated_at: mockNow };

export const mockMobileSuitGundam: WorkCardEntity = {
  ...timestamps,
  continuity: mockUniversalCenturyRef,
  end_date: '1980-01-26',
  slug: 'mobile-suit-gundam',
  start_date: '1979-04-07',
  title: 'Mobile Suit Gundam',
  title_ja: '機動戦士ガンダム',
  work_type: 'tv_series',
};

export const mockMobileSuitGundamI: WorkCardEntity = {
  ...timestamps,
  continuity: mockUniversalCenturyRef,
  end_date: null,
  slug: 'mobile-suit-gundam-i',
  start_date: '1981-03-04',
  title: 'Mobile Suit Gundam I',
  title_ja: '劇場版 機動戦士ガンダム',
  work_type: 'film',
};

export const mockTheOrigin: WorkCardEntity = {
  ...timestamps,
  continuity: mockUniversalCenturyRef,
  end_date: '2018-05-05',
  slug: 'mobile-suit-gundam-the-origin',
  start_date: '2015-02-28',
  title: 'Mobile Suit Gundam: The Origin',
  title_ja: '機動戦士ガンダム THE ORIGIN',
  work_type: 'ova',
};

export const mockTheOriginAdvent: WorkCardEntity = {
  ...timestamps,
  continuity: mockUniversalCenturyRef,
  end_date: '2019-08-11',
  slug: 'mobile-suit-gundam-the-origin-advent-of-the-red-comet',
  start_date: '2019-04-29',
  title: 'Mobile Suit Gundam: The Origin Advent of the Red Comet',
  title_ja: '機動戦士ガンダム THE ORIGIN 前夜 赤い彗星',
  work_type: 'tv_series',
};

export const mockItMoves: WorkCardEntity = {
  ...timestamps,
  // A documentary; the wiki gives its era as "Not Applicable".
  continuity: null,
  end_date: '2021-03-30',
  slug: 'it-moves-gundam-follow-your-dreams',
  start_date: '2020-03-23',
  title: 'It Moves? Gundam, Follow Your Dreams!',
  title_ja: '動くのか？ガンダム 夢への挑戦！',
  work_type: 'other',
};

/** @description Every work, in the API's order: first released first. */
export const mockWorks: readonly WorkCardEntity[] = [
  mockMobileSuitGundam,
  mockMobileSuitGundamI,
  mockTheOrigin,
  mockTheOriginAdvent,
  mockItMoves,
];

function compilation(
  direction: RelatedWorkEntity['direction'],
  work: WorkCardEntity,
  source: RelatedWorkEntity['source'],
): RelatedWorkEntity {
  return {
    created_at: mockNow,
    direction,
    relation_type: 'compilation_of',
    source,
    work,
  };
}

function detail(
  card: WorkCardEntity,
  relations: RelatedWorkEntity[],
): WorkDetailEntity {
  return { ...card, parent_work: null, relations };
}

/** @description Each work's detail, keyed by its current slug. */
export const mockWorkDetails: Readonly<Record<string, WorkDetailEntity>> = {
  [mockMobileSuitGundam.slug]: detail(mockMobileSuitGundam, [
    compilation('incoming', mockMobileSuitGundamI, mockSources.mobileSuitGundamI),
  ]),
  [mockMobileSuitGundamI.slug]: detail(mockMobileSuitGundamI, [
    compilation('outgoing', mockMobileSuitGundam, mockSources.mobileSuitGundamI),
  ]),
  [mockTheOrigin.slug]: detail(mockTheOrigin, [
    compilation('incoming', mockTheOriginAdvent, mockSources.theOriginAdvent),
  ]),
  [mockTheOriginAdvent.slug]: detail(mockTheOriginAdvent, [
    compilation('outgoing', mockTheOrigin, mockSources.theOriginAdvent),
  ]),
  [mockItMoves.slug]: detail(mockItMoves, []),
};

/**
 * @description Finds a work's detail by slug, as `GET /api/works/{work_slug}` does.
 * @returns `undefined` for an unknown slug, which the route answers with a 404.
 */
export function findWorkMock(slug: string): WorkDetailEntity | undefined {
  return mockWorkDetails[slug];
}
