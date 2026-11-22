// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`).
//
// The cards and refs for characters, organizations and designers. They live apart from
// the detail fixtures, which list suits, so that `mobileSuitMocks.ts` can name its pilots
// and credits without an import cycle.
import type {
  CharacterCardEntity,
  CharacterRefEntity,
  MechanicalDesignerCardEntity,
  MechanicalDesignerRefEntity,
  OrganizationCardEntity,
  OrganizationRefEntity,
} from '@/api';

import { mockNow } from './catalogMocks';

const timestamps = { created_at: mockNow, updated_at: mockNow };

/** @description Just a card's `name` and `slug`, as the API's refs carry them. */
export function toRef<T extends { name: string; slug: string }>({
  name,
  slug,
}: T): Pick<T, 'name' | 'slug'> {
  return { name, slug };
}

/**
 * @description Finds a row by its current or an old slug, as every detail route does
 * (D2). A current slug wins: it is looked up before the redirects, so an old slug that
 * another row now holds finds that row.
 * @returns `undefined` for an unknown slug, which the route answers with a 404.
 */
export function findBySlugOrRedirect<T>({
  byCurrentSlug,
  redirects,
  slug,
}: {
  byCurrentSlug: Readonly<Record<string, T>>;
  redirects: Readonly<Record<string, string>>;
  slug: string;
}): T | undefined {
  const redirectedTo = redirects[slug];
  return (
    byCurrentSlug[slug] ??
    (redirectedTo === undefined ? undefined : byCurrentSlug[redirectedTo])
  );
}

export const mockAmuroRay: CharacterCardEntity = {
  ...timestamps,
  name: 'Amuro Ray',
  name_ja: 'アムロ・レイ',
  slug: 'amuro-ray',
};

export const mockAmuroRayOrigin: CharacterCardEntity = {
  ...timestamps,
  // NOTE: the Origin's Amuro has a page of his own, under the same name.
  name: 'Amuro Ray',
  name_ja: 'アムロ・レイ',
  slug: 'amuro-ray-origin',
};

/** @description Every character, in the API's order: by name, then by when it was stored. */
export const mockCharacters: readonly CharacterCardEntity[] = [
  mockAmuroRay,
  mockAmuroRayOrigin,
];

/** @description Old slugs that answer for a character, as `character_slug_redirects` holds. */
export const mockCharacterSlugRedirects: Readonly<Record<string, string>> = {
  // The wiki's `Amuro` redirect page.
  amuro: mockAmuroRay.slug,
};

export const mockAmuroRayRef: CharacterRefEntity = toRef(mockAmuroRay);
export const mockAmuroRayOriginRef: CharacterRefEntity = toRef(mockAmuroRayOrigin);

export const mockEarthFederation: OrganizationCardEntity = {
  ...timestamps,
  name: 'Earth Federation',
  parent_organization: null,
  slug: 'earth-federation',
};

export const mockPrincipalityOfZeon: OrganizationCardEntity = {
  ...timestamps,
  name: 'Principality of Zeon',
  parent_organization: null,
  slug: 'principality-of-zeon',
};

export const mockZeonic: OrganizationCardEntity = {
  ...timestamps,
  name: 'Zeonic',
  parent_organization: null,
  slug: 'zeonic',
};

/** @description Every organization, in the API's order: by name. */
export const mockOrganizations: readonly OrganizationCardEntity[] = [
  mockEarthFederation,
  mockPrincipalityOfZeon,
  mockZeonic,
];

/** @description Old slugs that answer for an organization, as its redirect table holds. */
export const mockOrganizationSlugRedirects: Readonly<Record<string, string>> = {
  // The wiki's `Earth Federation (Universal Century)` redirect page.
  'earth-federation-universal-century': mockEarthFederation.slug,
};

export const mockEarthFederationRef: OrganizationRefEntity = toRef(mockEarthFederation);
export const mockPrincipalityOfZeonRef: OrganizationRefEntity =
  toRef(mockPrincipalityOfZeon);
export const mockZeonicRef: OrganizationRefEntity = toRef(mockZeonic);

export const mockHajimeKatoki: MechanicalDesignerCardEntity = {
  ...timestamps,
  name: 'Hajime Katoki',
  name_ja: 'カトキハジメ',
  slug: 'hajime-katoki',
};

export const mockKunioOkawara: MechanicalDesignerCardEntity = {
  ...timestamps,
  name: 'Kunio Okawara',
  // NOTE: the page's spacing, kept as written.
  name_ja: '大河原 邦男',
  slug: 'kunio-okawara',
};

export const mockMasakiKawahara: MechanicalDesignerCardEntity = {
  ...timestamps,
  // NOTE: credited on the RX-78F00 page, but with no page of his own.
  name: 'Masaki Kawahara',
  name_ja: null,
  slug: 'masaki-kawahara',
};

/** @description Every designer, in the API's order: by name. */
export const mockMechanicalDesigners: readonly MechanicalDesignerCardEntity[] = [
  mockHajimeKatoki,
  mockKunioOkawara,
  mockMasakiKawahara,
];

/** @description Old slugs that answer for a designer, as its redirect table holds. */
export const mockMechanicalDesignerSlugRedirects: Readonly<Record<string, string>> = {
  // The wiki's `Katoki Hajime` redirect page.
  'katoki-hajime': mockHajimeKatoki.slug,
};

export const mockHajimeKatokiRef: MechanicalDesignerRefEntity = toRef(mockHajimeKatoki);
export const mockKunioOkawaraRef: MechanicalDesignerRefEntity = toRef(mockKunioOkawara);
export const mockMasakiKawaharaRef: MechanicalDesignerRefEntity =
  toRef(mockMasakiKawahara);
