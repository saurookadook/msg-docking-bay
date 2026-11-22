// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`).
import type {
  ArmamentListingEntity,
  ArmamentMount,
  ArmamentRefEntity,
  DesignerCreditEntity,
  EquipmentListingEntity,
  EquipmentRefEntity,
  MaterialListingEntity,
  MaterialRefEntity,
  MechanicalDesignerRefEntity,
  MobileSuitAppearanceCardEntity,
  MobileSuitCardEntity,
  MobileSuitDetailEntity,
  MobileSuitOrganizationRole,
  MobileSuitSpecSheetEntity,
  OrganizationCreditEntity,
  OrganizationRefEntity,
  PilotCreditEntity,
  PowerplantListingEntity,
  PowerplantRefEntity,
  RelatedMobileSuitEntity,
  SourceCitationEntity,
  WorkAppearanceEntity,
  WorkCardEntity,
  WorkRefEntity,
} from '@/api';

import type { Nullable } from '@/types';

import { mockNow, mockSources, mockUniversalCenturyRef } from './catalogMocks';
import {
  findBySlugOrRedirect,
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

const noParts = {
  armaments: [],
  equipment: [],
  materials: [],
  powerplants: [],
} satisfies Partial<MobileSuitSpecSheetEntity>;

function specSheet(
  source: SourceCitationEntity,
  values: Partial<MobileSuitSpecSheetEntity>,
): MobileSuitSpecSheetEntity {
  return {
    ...timestamps,
    ...noSpecs,
    ...noParts,
    configuration: null,
    inherited_fields: [],
    inherited_parts: [],
    source,
    ...values,
  };
}

// Parts with their own wiki article; the seed also stores their page IDs.
const beamSaber: ArmamentRefEntity = { name: 'Beam Saber', slug: 'beam-saber' };
const coreBlockSystem: EquipmentRefEntity = {
  name: 'Core Block System',
  slug: 'core-block-system',
};
const lunaTitaniumAlloy: MaterialRefEntity = {
  name: 'Luna Titanium Alloy',
  slug: 'luna-titanium-alloy',
};
const minovskyReactor: PowerplantRefEntity = {
  name: 'Minovsky Ultracompact Fusion Reactor',
  slug: 'minovsky-ultracompact-fusion-reactor',
};

function armament(
  name: string,
  slug: string,
  mount: ArmamentMount,
  values: Partial<ArmamentListingEntity> = {},
): ArmamentListingEntity {
  return {
    armament: { name, slug },
    created_at: mockNow,
    mount,
    note: null,
    quantity_max: null,
    quantity_min: null,
    ...values,
  };
}

function armamentRef(
  ref: ArmamentRefEntity,
  mount: ArmamentMount,
  values: Partial<ArmamentListingEntity> = {},
): ArmamentListingEntity {
  return armament(ref.name, ref.slug, mount, values);
}

function equipment(
  ref: EquipmentRefEntity,
  values: Partial<EquipmentListingEntity> = {},
): EquipmentListingEntity {
  return {
    created_at: mockNow,
    equipment: ref,
    fit: 'standard',
    note: null,
    ...values,
  };
}

function armor(ref: MaterialRefEntity): MaterialListingEntity {
  return { created_at: mockNow, material: ref, material_use: 'armor', note: null };
}

function powerplant(ref: PowerplantRefEntity): PowerplantListingEntity {
  return {
    created_at: mockNow,
    note: null,
    powerplant: ref,
    quantity_max: null,
    quantity_min: null,
  };
}

/** @description Counts as the infobox gives them: `2 ×` sets both, `1-2 ×` a range. */
const twice = { quantity_max: 2, quantity_min: 2 };
const onceOrTwice = { quantity_max: 2, quantity_min: 1 };

// In the API's order: by mount, then by name in the database's collation.
const rx782Parts = {
  armaments: [
    armament('60mm Vulcan Gun', '60mm-vulcan-gun', 'fixed', twice),
    armamentRef(beamSaber, 'handheld', { ...twice, note: '2 x Beam Javelin' }),
    armament(
      'BOWA-XBR-M-79-07G Beam Rifle',
      'bowa-xbr-m-79-07g-beam-rifle',
      'handheld',
    ),
    armament(
      'BLASH-XHB-L-03/N-STD 380mm Hyper Bazooka',
      'blash-xhb-l-03-n-std-380mm-hyper-bazooka',
      'optional_handheld',
      onceOrTwice,
    ),
  ],
  equipment: [
    equipment(coreBlockSystem),
    equipment(
      { name: 'Magnet Coating', slug: 'magnet-coating' },
      { note: 'field upgrade' },
    ),
  ],
  materials: [armor(lunaTitaniumAlloy)],
  powerplants: [powerplant(minovskyReactor)],
} satisfies Partial<MobileSuitSpecSheetEntity>;

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

/** @description A pilot credit; `work` is null when the infobox gives the pairing none. */
function createPilotCreditMock({
  character,
  source,
  work,
}: {
  character: PilotCreditEntity['character'];
  source: SourceCitationEntity;
  work: Nullable<WorkCardEntity>;
}): PilotCreditEntity {
  return {
    character,
    created_at: mockNow,
    source,
    work: work === null ? null : toWorkRef(work),
  };
}

// NOTE: none of the seeded organization links is tagged with a work, so `work` is null.
function createOrganizationCreditMock({
  organization,
  role,
  source,
}: {
  organization: OrganizationRefEntity;
  role: MobileSuitOrganizationRole;
  source: SourceCitationEntity;
}): OrganizationCreditEntity {
  return { created_at: mockNow, organization, role, source, work: null };
}

function createDesignerCreditMock({
  mechanicalDesigner,
  source,
}: {
  mechanicalDesigner: MechanicalDesignerRefEntity;
  source: SourceCitationEntity;
}): DesignerCreditEntity {
  return { created_at: mockNow, mechanical_designer: mechanicalDesigner, source };
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
    designers: [
      createDesignerCreditMock({
        mechanicalDesigner: mockKunioOkawaraRef,
        source: mockSources.rx782Gundam,
      }),
    ],
    organizations: [
      createOrganizationCreditMock({
        organization: mockEarthFederationRef,
        role: 'manufacturer',
        source: mockSources.rx782Gundam,
      }),
    ],
    pilots: [
      createPilotCreditMock({
        character: mockAmuroRayRef,
        source: mockSources.rx782Gundam,
        work: mockMobileSuitGundam,
      }),
    ],
    relations: [
      alternateVersion('incoming', mockRx7802Gundam, mockSources.rx7802Gundam),
      alternateVersion('incoming', mockRx78f00Gundam, mockSources.rx78f00Gundam),
    ],
    spec_sheets: [
      specSheet(mockSources.rx782Gundam, {
        ...rx782BaseSpecs,
        ...rx782Parts,
        turn_time_s: 1.5,
      }),
      // The infobox gives "1.1~after magnet coating upgrade"; the rest comes from the
      // base sheet of the same source, parts included, since the infobox lists them once.
      specSheet(mockSources.rx782Gundam, {
        ...rx782BaseSpecs,
        ...rx782Parts,
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
        inherited_parts: ['armaments', 'equipment', 'materials', 'powerplants'],
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
      createDesignerCreditMock({
        mechanicalDesigner: mockHajimeKatokiRef,
        source: mockSources.rx7802Gundam,
      }),
      createDesignerCreditMock({
        mechanicalDesigner: mockKunioOkawaraRef,
        source: mockSources.rx7802Gundam,
      }),
    ],
    organizations: [],
    // The infobox gives this pairing no work.
    pilots: [
      createPilotCreditMock({
        character: mockAmuroRayOriginRef,
        source: mockSources.rx7802Gundam,
        work: null,
      }),
    ],
    relations: [
      alternateVersion('outgoing', mockRx782Gundam, mockSources.rx7802Gundam),
    ],
    spec_sheets: [
      specSheet(mockSources.rx7802Gundam, {
        armaments: [
          armamentRef(beamSaber, 'fixed', onceOrTwice),
          armament('Vulcan Gun', 'vulcan-gun', 'fixed', twice),
          armament('Beam Rifle', 'beam-rifle', 'handheld'),
          armament('Shoulder Cannon', 'shoulder-cannon', 'optional_fixed'),
        ],
        equipment: [equipment(coreBlockSystem, { note: 'refit' })],
        head_height_m: 18,
        materials: [armor(lunaTitaniumAlloy)],
        powerplants: [powerplant(minovskyReactor)],
      }),
    ],
  },
  [mockRx78f00Gundam.slug]: {
    ...mockRx78f00Gundam,
    appearances: [
      appearance(mockItMoves, mockSources.rx78f00Gundam, { is_debut: true }),
    ],
    designers: [
      createDesignerCreditMock({
        mechanicalDesigner: mockMasakiKawaharaRef,
        source: mockSources.rx78f00Gundam,
      }),
    ],
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
    designers: [
      createDesignerCreditMock({
        mechanicalDesigner: mockKunioOkawaraRef,
        source: mockSources.ms06fZakuII,
      }),
    ],
    organizations: [
      createOrganizationCreditMock({
        organization: mockZeonicRef,
        role: 'manufacturer',
        source: mockSources.ms06fZakuII,
      }),
      createOrganizationCreditMock({
        organization: mockPrincipalityOfZeonRef,
        role: 'operator',
        source: mockSources.ms06fZakuII,
      }),
    ],
    pilots: [],
    relations: [],
    spec_sheets: [
      // The infobox names no powerplant.
      specSheet(mockSources.ms06fZakuII, {
        armaments: [
          armament('Shoulder Shield', 'shoulder-shield', 'fixed'),
          armament('120mm Machine Gun', '120mm-machine-gun', 'handheld'),
          armament('Heat Hawk', 'heat-hawk', 'handheld'),
          armament('3-tube Missile Pod', '3-tube-missile-pod', 'optional_fixed', twice),
          armament(
            'MMP-80 90mm Machine Gun',
            'mmp-80-90mm-machine-gun',
            'optional_handheld',
          ),
        ],
        empty_weight_kg: 58100,
        generator_output_kw: 951,
        gross_weight_kg: 73300,
        head_height_m: 17.5,
        materials: [
          armor({ name: 'Super Hard Steel Alloy', slug: 'super-hard-steel-alloy' }),
        ],
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
  return findBySlugOrRedirect({
    byCurrentSlug: mockMobileSuitDetails,
    redirects: mockMobileSuitSlugRedirects,
    slug,
  });
}

/**
 * @description The suits with a credit that `matches`, each with those credits, in
 * `mockMobileSuits` order (by name). The people fixtures derive their suit lists from
 * it, so the suit fixtures stay the one copy of every credit.
 */
export function creditsBySuit<Credit>({
  credits,
  matches,
}: {
  credits: (detail: MobileSuitDetailEntity) => readonly Credit[];
  matches: (credit: Credit) => boolean;
}): { card: MobileSuitCardEntity; credits: Credit[] }[] {
  return mockMobileSuits.flatMap((card) => {
    const detail = mockMobileSuitDetails[card.slug];
    const found = detail === undefined ? [] : credits(detail).filter(matches);
    return found.length === 0 ? [] : [{ card, credits: found }];
  });
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
