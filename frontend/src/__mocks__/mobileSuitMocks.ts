// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`).
import type {
  DesignerCreditEntity,
  MechanicalDesignerRefEntity,
  MobileSuitAppearanceCardEntity,
  MobileSuitCardEntity,
  MobileSuitDetailEntity,
  MobileSuitOrganizationRole,
  MobileSuitSpecSheetEntity,
  OrganizationCreditEntity,
  OrganizationRefEntity,
  PilotCreditEntity,
  RelatedMobileSuitEntity,
  SourceCitationEntity,
  WorkAppearanceEntity,
  WorkCardEntity,
  WorkRefEntity,
} from '@/api';

import { mockNow, mockSources, mockUniversalCenturyRef } from './catalogMocks';
import {
  mockAmuroRayOriginRef,
  mockAmuroRayRef,
  mockEarthFederationRef,
  mockHajimeKatokiRef,
  mockKunioOkawaraRef,
  mockMasakiKawaharaRef,
  mockPrincipalityOfZeonRef,
  mockZeonicRef,
} from './peopleMocks';
import {
  mockItMoves,
  mockMobileSuitGundam,
  mockMobileSuitGundamI,
  mockTheOrigin,
  mockTheOriginAdvent,
} from './workMocks';

const timestamps = { created_at: mockNow, updated_at: mockNow };

export const mockRx782Gundam: MobileSuitCardEntity = {
  ...timestamps,
  continuity: mockUniversalCenturyRef,
  model_number: 'RX-78-2',
  name: 'Gundam',
  name_ja: 'ガンダム',
  slug: 'rx-78-2-gundam',
  unit_type: 'suit',
};

export const mockRx7802Gundam: MobileSuitCardEntity = {
  ...timestamps,
  continuity: mockUniversalCenturyRef,
  model_number: 'RX-78-02',
  name: 'Gundam',
  name_ja: 'ガンダム',
  slug: 'rx-78-02-gundam',
  unit_type: 'suit',
};

export const mockRx78f00Gundam: MobileSuitCardEntity = {
  ...timestamps,
  // The life-size statue at Gundam Factory Yokohama: no era.
  continuity: null,
  model_number: 'RX-78F00',
  name: 'Gundam',
  name_ja: 'ガンダム',
  slug: 'rx-78f00-gundam',
  unit_type: 'suit',
};

export const mockZakuII: MobileSuitCardEntity = {
  ...timestamps,
  continuity: mockUniversalCenturyRef,
  model_number: 'MS-06F',
  name: 'Zaku II',
  name_ja: '量産型ザクII',
  slug: 'ms-06f-zaku-ii',
  unit_type: 'suit',
};

/** @description Every suit, in the API's order: by name, then by when it was stored. */
export const mockMobileSuits: readonly MobileSuitCardEntity[] = [
  mockRx782Gundam,
  mockRx7802Gundam,
  mockRx78f00Gundam,
  mockZakuII,
];

/** @description Old slugs that answer for a suit, as `mobile_suit_slug_redirects` holds. */
export const mockMobileSuitSlugRedirects: Readonly<Record<string, string>> = {
  // The wiki's `RX-78-2` redirect page.
  'rx-78-2': mockRx782Gundam.slug,
};

const noSpecs = {
  empty_weight_kg: null,
  generator_output_kw: null,
  gross_weight_kg: null,
  head_height_m: null,
  max_acceleration_g: null,
  max_speed_kmh: null,
  overall_height_m: null,
  sensor_range_m: null,
  total_thrust_kg: null,
  turn_time_s: null,
} satisfies Partial<MobileSuitSpecSheetEntity>;

function specSheet(
  source: SourceCitationEntity,
  values: Partial<MobileSuitSpecSheetEntity>,
): MobileSuitSpecSheetEntity {
  return {
    ...timestamps,
    ...noSpecs,
    configuration: null,
    inherited_fields: [],
    source,
    ...values,
  };
}

const rx782BaseSpecs = {
  empty_weight_kg: 43400,
  generator_output_kw: 1380,
  gross_weight_kg: 60000,
  head_height_m: 18,
  max_acceleration_g: 0.93,
  max_speed_kmh: 165,
  sensor_range_m: 5700,
  total_thrust_kg: 55480,
} satisfies Partial<MobileSuitSpecSheetEntity>;

function appearance(
  work: WorkCardEntity,
  source: SourceCitationEntity,
  values: Partial<WorkAppearanceEntity> = {},
): WorkAppearanceEntity {
  return {
    created_at: mockNow,
    first_episode: null,
    is_debut: false,
    last_episode: null,
    source,
    work,
    ...values,
  };
}

function alternateVersion(
  direction: RelatedMobileSuitEntity['direction'],
  mobileSuit: MobileSuitCardEntity,
  source: SourceCitationEntity,
): RelatedMobileSuitEntity {
  return {
    created_at: mockNow,
    direction,
    mobile_suit: mobileSuit,
    relation_type: 'alternate_version_of',
    source,
  };
}

/** @description Just a work's `slug` and `title`, as a credit's `work` carries them. */
export function toWorkRef({ slug, title }: WorkCardEntity): WorkRefEntity {
  return { slug, title };
}

function pilot(
  character: PilotCreditEntity['character'],
  source: SourceCitationEntity,
  work: WorkCardEntity | null,
): PilotCreditEntity {
  return {
    character,
    created_at: mockNow,
    source,
    work: work === null ? null : toWorkRef(work),
  };
}

// None of the seeded organization links is tagged with a work.
function organization(
  ref: OrganizationRefEntity,
  role: MobileSuitOrganizationRole,
  source: SourceCitationEntity,
): OrganizationCreditEntity {
  return { created_at: mockNow, organization: ref, role, source, work: null };
}

function designer(
  ref: MechanicalDesignerRefEntity,
  source: SourceCitationEntity,
): DesignerCreditEntity {
  return { created_at: mockNow, mechanical_designer: ref, source };
}

/**
 * @description Each suit's detail, keyed by its current slug. Credits follow the API's
 * order: pilots by work (none last), organizations by role, designers by name.
 */
export const mockMobileSuitDetails: Readonly<Record<string, MobileSuitDetailEntity>> = {
  [mockRx782Gundam.slug]: {
    ...mockRx782Gundam,
    appearances: [
      appearance(mockMobileSuitGundam, mockSources.rx782Gundam, {
        first_episode: 1,
        is_debut: true,
        last_episode: 43,
      }),
      appearance(mockMobileSuitGundamI, mockSources.rx782Gundam),
    ],
    designers: [designer(mockKunioOkawaraRef, mockSources.rx782Gundam)],
    organizations: [
      organization(mockEarthFederationRef, 'manufacturer', mockSources.rx782Gundam),
    ],
    pilots: [pilot(mockAmuroRayRef, mockSources.rx782Gundam, mockMobileSuitGundam)],
    relations: [
      alternateVersion('incoming', mockRx7802Gundam, mockSources.rx7802Gundam),
      alternateVersion('incoming', mockRx78f00Gundam, mockSources.rx78f00Gundam),
    ],
    spec_sheets: [
      specSheet(mockSources.rx782Gundam, { ...rx782BaseSpecs, turn_time_s: 1.5 }),
      // The infobox gives "1.1~after magnet coating upgrade"; the rest comes from the
      // base sheet of the same source.
      specSheet(mockSources.rx782Gundam, {
        ...rx782BaseSpecs,
        configuration: 'Magnet Coating',
        inherited_fields: [
          'empty_weight_kg',
          'generator_output_kw',
          'gross_weight_kg',
          'head_height_m',
          'max_acceleration_g',
          'max_speed_kmh',
          'sensor_range_m',
          'total_thrust_kg',
        ],
        turn_time_s: 1.1,
      }),
    ],
  },
  [mockRx7802Gundam.slug]: {
    ...mockRx7802Gundam,
    // The article says it debuts in the manga, which the seed leaves out.
    appearances: [
      appearance(mockTheOrigin, mockSources.rx7802Gundam),
      appearance(mockTheOriginAdvent, mockSources.rx7802Gundam),
    ],
    // Okawara for the manga, Katoki for the anime.
    designers: [
      designer(mockHajimeKatokiRef, mockSources.rx7802Gundam),
      designer(mockKunioOkawaraRef, mockSources.rx7802Gundam),
    ],
    organizations: [],
    // The infobox gives this pairing no work.
    pilots: [pilot(mockAmuroRayOriginRef, mockSources.rx7802Gundam, null)],
    relations: [
      alternateVersion('outgoing', mockRx782Gundam, mockSources.rx7802Gundam),
    ],
    spec_sheets: [specSheet(mockSources.rx7802Gundam, { head_height_m: 18 })],
  },
  [mockRx78f00Gundam.slug]: {
    ...mockRx78f00Gundam,
    appearances: [
      appearance(mockItMoves, mockSources.rx78f00Gundam, { is_debut: true }),
    ],
    designers: [designer(mockMasakiKawaharaRef, mockSources.rx78f00Gundam)],
    organizations: [],
    pilots: [],
    relations: [
      alternateVersion('outgoing', mockRx782Gundam, mockSources.rx78f00Gundam),
    ],
    spec_sheets: [
      specSheet(mockSources.rx78f00Gundam, {
        gross_weight_kg: 25000,
        head_height_m: 18,
      }),
    ],
  },
  [mockZakuII.slug]: {
    ...mockZakuII,
    appearances: [
      appearance(mockMobileSuitGundam, mockSources.ms06fZakuII, { is_debut: true }),
      appearance(mockMobileSuitGundamI, mockSources.ms06fZakuII),
    ],
    designers: [designer(mockKunioOkawaraRef, mockSources.ms06fZakuII)],
    organizations: [
      organization(mockZeonicRef, 'manufacturer', mockSources.ms06fZakuII),
      organization(mockPrincipalityOfZeonRef, 'operator', mockSources.ms06fZakuII),
    ],
    pilots: [],
    relations: [],
    spec_sheets: [
      specSheet(mockSources.ms06fZakuII, {
        empty_weight_kg: 58100,
        generator_output_kw: 951,
        gross_weight_kg: 73300,
        head_height_m: 17.5,
        max_acceleration_g: 0.59,
        max_speed_kmh: 88,
        sensor_range_m: 3200,
        total_thrust_kg: 43000,
        turn_time_s: 1.7,
      }),
    ],
  },
};

/**
 * @description Finds a suit's detail by its current or an old slug, as
 * `GET /api/mobile-suits/{mobile_suit_slug}` does. An old slug returns the renamed suit,
 * whose `slug` is the current one (D2).
 * @returns `undefined` for an unknown slug, which the route answers with a 404.
 */
export function findMobileSuitMock(slug: string): MobileSuitDetailEntity | undefined {
  return (
    mockMobileSuitDetails[slug] ??
    mockMobileSuitDetails[mockMobileSuitSlugRedirects[slug] ?? '']
  );
}

/**
 * @description The suits in one work, as `GET /api/works/{work_slug}/mobile-suits` lists
 * them: debuts first, then in `mockMobileSuits` order (by name).
 */
export function findWorkMobileSuitsMock(
  workSlug: string,
): MobileSuitAppearanceCardEntity[] {
  const cards = mockMobileSuits.flatMap((card) => {
    const found = mockMobileSuitDetails[card.slug]?.appearances.find(
      ({ work }) => work.slug === workSlug,
    );
    return found === undefined
      ? []
      : [
          {
            ...card,
            first_episode: found.first_episode,
            is_debut: found.is_debut,
            last_episode: found.last_episode,
          },
        ];
  });
  return cards.toSorted((a, b) => Number(b.is_debut) - Number(a.is_debut));
}
