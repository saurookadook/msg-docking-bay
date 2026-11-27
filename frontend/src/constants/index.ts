import type { MobileSuitOrganizationRole, SourceKind, UnitType, WorkType } from '@/api';

/**
 * @description Base URL that `safeFetch` resolves `/api/...` paths against.
 * @note Empty on purpose: the browser calls the API on its own origin, and the reverse
 * proxy routes `/api` to the backend (ENV-40), so no API host is baked into the build.
 */
export const BASE_API_URL = '';

/**
 * @description The `limit` a list route uses when a request gives none.
 * @note Mirrors `DEFAULT_PAGE_SIZE` in `backend/constants/pagination.py`; change both.
 */
export const DEFAULT_PAGE_SIZE = 50;

/**
 * @description The largest `limit` a list route accepts; a larger one is a 422.
 * @note Mirrors `MAX_PAGE_SIZE` in `backend/constants/pagination.py`; change both.
 */
export const MAX_PAGE_SIZE = 100;

/**
 * @description The longest `q` a search accepts; a longer one is a 422.
 * @note Mirrors `MAX_SEARCH_LENGTH` in `backend/constants/pagination.py`; change both.
 */
export const MAX_SEARCH_LENGTH = 100;

/**
 * @description The per-kind `limit` the catalog search uses when a request gives none.
 * @note Mirrors `SEARCH_DEFAULT_LIMIT` in `backend/constants/pagination.py`; change both.
 */
export const SEARCH_DEFAULT_LIMIT = 5;

/**
 * @description The largest per-kind `limit` the catalog search accepts.
 * @note Mirrors `SEARCH_MAX_LIMIT` in `backend/constants/pagination.py`; change both.
 */
export const SEARCH_MAX_LIMIT = 20;

/**
 * @description The `localStorage` key holding the chosen shift, as a JSON string.
 * @note `index.html` reads the same key before first paint; its test keeps the two in
 * step.
 */
export const SHIFT_LS_KEY = 'msgdb.shift';

/**
 * @description Every shift the deck can run: `auto` follows the OS color scheme, `day`
 * forces light and `night` forces dark.
 */
export const SHIFTS = ['auto', 'day', 'night'] as const;

/**
 * @description Every catalog entity kind with its own pages, in deck (nav) order, with
 * what each part of the app needs to know about it.
 * @note Adding a kind here is the whole change: `EntityKind`, `AppParams`, `entityPath`,
 * `EntityLink` and the nav all read this table. Set `isCommissioned` once the kind's
 * list page exists; until then its bay sign shows "Offline".
 */
export const ENTITY_KINDS = {
  mobileSuit: {
    listPath: '/mobile-suits',
    navLabel: 'Mobile Suits',
    isCommissioned: true,
    // NOTE: icons are original line drawings on a 16-unit grid (`EntityLink`).
    iconPath: 'M5 2h6l2 4v5l-2 3H5l-2-3V6zM5 7h6',
  },
  character: {
    listPath: '/characters',
    navLabel: 'Personnel',
    isCommissioned: true,
    iconPath: 'M8 2a3 3 0 1 1 0 6a3 3 0 1 1 0-6zM2 14c1-3 3-4 6-4s5 1 6 4',
  },
  organization: {
    listPath: '/organizations',
    navLabel: 'Organizations',
    isCommissioned: true,
    iconPath: 'M8 1l6 2v5c0 3-3 6-6 7c-3-1-6-4-6-7V3z',
  },
  work: {
    listPath: '/works',
    navLabel: 'Works',
    isCommissioned: true,
    iconPath: 'M2 3h12v10H2zM5 3v10M11 3v10M2 8h3M11 8h3',
  },
  mechanicalDesigner: {
    listPath: '/mechanical-designers',
    navLabel: 'Designers',
    isCommissioned: true,
    iconPath: 'M8 1v3M8 4l-5 11M8 4l5 11M5 10h6',
  },
} as const satisfies Record<
  string,
  { listPath: string; navLabel: string; isCommissioned: boolean; iconPath: string }
>;

/**
 * @description Each unit type the API knows, in its order, with the label the rosters
 * and filters show.
 * @note Its keys are also the values `unit_type` accepts; mock mode answers any other
 * with the API's 422.
 */
export const UNIT_TYPE_LABELS = {
  suit: 'Mobile Suit',
  armor: 'Mobile Armor',
  fighter: 'Fighter',
  man_machine: 'Man Machine',
  worker: 'Mobile Worker',
  pod: 'Mobile Pod',
  doll: 'Mobile Doll',
} as const satisfies Record<UnitType, string>;

/**
 * @description Each work type the API knows, in its order, with the label the rosters
 * and filters show.
 * @note Its keys are also the values `work_type` accepts.
 */
export const WORK_TYPE_LABELS = {
  tv_series: 'TV series',
  film: 'Film',
  ova: 'OVA',
  ona: 'ONA',
  manga: 'Manga',
  novel: 'Novel',
  video_game: 'Video game',
  other: 'Other',
} as const satisfies Record<WorkType, string>;

/**
 * @description Each role an organization plays for a suit, in the API's order, with the
 * label its credits show.
 * @note Its keys are also the values an organization's suit list's `role` accepts.
 */
export const ORGANIZATION_ROLE_LABELS = {
  manufacturer: 'Manufacturer',
  operator: 'Operator',
  developer: 'Developer',
} as const satisfies Record<MobileSuitOrganizationRole, string>;

/** @description The unit types as filter select options, in the API's order. */
export const UNIT_TYPE_OPTIONS = Object.entries(UNIT_TYPE_LABELS).map(
  ([value, label]) => ({
    label,
    value,
  }),
);

/** @description The work types as filter select options, in the API's order. */
export const WORK_TYPE_OPTIONS = Object.entries(WORK_TYPE_LABELS).map(
  ([value, label]) => ({
    label,
    value,
  }),
);

/** @description How long the roster search waits after the last keystroke to search. */
export const SEARCH_DEBOUNCE_MS = 300;

/** @description The name each kind of source is credited by. */
export const SOURCE_KIND_LABELS = {
  fandom_page: 'Gundam Wiki',
  wikidata_item: 'Wikidata',
  wikipedia_en_page: 'Wikipedia (EN)',
  wikipedia_ja_page: 'Wikipedia (JA)',
} as const satisfies Record<SourceKind, string>;
