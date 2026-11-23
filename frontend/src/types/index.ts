import type { ENTITY_KINDS, SHIFTS } from '@/constants';

export type Nullable<T> = T | null;

/** @description A deck shift, which picks the color scheme (`SHIFTS`). */
export type Shift = (typeof SHIFTS)[number];

/** @description A kind of catalog entity that has its own pages (`ENTITY_KINDS`). */
export type EntityKind = keyof typeof ENTITY_KINDS;

/**
 * @description Every route param in the app (REACT-27). Each is the entity's current slug.
 * @note Slugs, not IDs: the API's public key is the slug (`catalog-read-api.md` D2).
 */
export type AppParams = {
  characterSlug?: string;
  mechanicalDesignerSlug?: string;
  mobileSuitSlug?: string;
  organizationSlug?: string;
  workSlug?: string;
};
