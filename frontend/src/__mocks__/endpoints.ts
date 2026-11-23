import { Response as MirageResponse, type Request } from 'miragejs';

import type { PageMeta, paths, ValidationError } from '@/api';
import {
  DEFAULT_PAGE_SIZE,
  MAX_PAGE_SIZE,
  MAX_SEARCH_LENGTH,
  SEARCH_DEFAULT_LIMIT,
  SEARCH_MAX_LIMIT,
} from '@/constants';
import type { Nullable } from '@/types';

import { findCharacterMock } from './characterMocks';
import { mockContinuitiesListResponse } from './continuityMocks';
import { mockHealthCheckResponse } from './healthMocks';
import {
  findMechanicalDesignerMobileSuitsMock,
  findMechanicalDesignerMock,
} from './mechanicalDesignerMocks';
import {
  findMobileSuitMock,
  findWorkMobileSuitsMock,
  mockMobileSuits,
} from './mobileSuitMocks';
import {
  findOrganizationMobileSuitsMock,
  findOrganizationMock,
} from './organizationMocks';
import {
  mockCharacters,
  mockMechanicalDesigners,
  mockOrganizations,
} from './peopleMocks';
import { searchList } from './search';
import { findWorkMock, mockWorks } from './workMocks';

/** @description The API's paths that have a `GET` operation. */
export type ApiGetPath = {
  [P in keyof paths]: paths[P] extends { get: object } ? P : never;
}[keyof paths];

/** @description The JSON body of a `GET` to `P` that succeeds with a 200. */
export type OkBody<P extends ApiGetPath> =
  paths[P]['get']['responses'][200]['content']['application/json'];

/**
 * @description One mocked route: an OpenAPI path from the generated contract, and a
 * handler that returns that path's 200 body, or a `MirageResponse` for an error the
 * route can give (a 404 for an unknown slug, a 422 for a bad page).
 */
export type EndpointConfig<P extends ApiGetPath> = {
  path: P;
  handler: (request: Request) => OkBody<P> | MirageResponse;
};

/**
 * @description An `EndpointConfig` for any one path. Each config is checked against its
 * own path, so a handler can't return another route's body.
 */
export type AnyEndpointConfig = { [P in ApiGetPath]: EndpointConfig<P> }[ApiGetPath];

/**
 * @description Turns an OpenAPI path into a Mirage route under the `api` namespace that
 * `makeMirageServer` sets: it drops the leading `/api` and turns `{param}` into `:param`.
 * @example
 * ```ts
 * buildRoutePath('/api/mobile-suits/{mobile_suit_slug}'); // '/mobile-suits/:mobile_suit_slug'
 * ```
 */
export function buildRoutePath(path: string): string {
  const routePath = path.replace(/^\/api(?=\/|$)/, '').replaceAll(/\{(\w+)\}/g, ':$1');
  return routePath === '' ? '/' : routePath;
}

type QueryValue = Request['queryParams'][string];

/**
 * @description Reads one integer page parameter as FastAPI validates it, returning the
 * value or the same error FastAPI reports (FAPI-23's `loc`, `msg` and `type`).
 */
function readPageParam(
  name: 'limit' | 'offset',
  value: QueryValue,
  { fallback, min, max }: { fallback: number; min: number; max?: number },
): number | ValidationError {
  if (value === undefined || value === null) return fallback;
  const loc = ['query', name];
  const parsed =
    typeof value === 'string' && /^-?\d+$/.test(value.trim()) ? Number(value) : NaN;
  if (!Number.isInteger(parsed)) {
    return {
      loc,
      msg: 'Input should be a valid integer, unable to parse string as an integer',
      type: 'int_parsing',
    };
  }
  if (parsed < min) {
    return {
      loc,
      msg: `Input should be greater than or equal to ${min}`,
      type: 'greater_than_equal',
    };
  }
  if (max !== undefined && parsed > max) {
    return {
      loc,
      msg: `Input should be less than or equal to ${max}`,
      type: 'less_than_equal',
    };
  }
  return parsed;
}

/**
 * @description Pages a list fixture the way the API does (D3 in
 * `docs/plans/catalog-read-api.md`): it reads `limit` and `offset` from the query, and
 * returns that page with its `meta`. An offset past the end gives an empty `data`.
 * @returns A 422 `MirageResponse`, with the API's body, for a `limit` outside
 * `1..MAX_PAGE_SIZE` or an `offset` that is negative or not an integer.
 */
export function paginate<T>(
  items: readonly T[],
  { queryParams }: Pick<Request, 'queryParams'>,
): { data: T[]; meta: PageMeta } | MirageResponse {
  const limit = readPageParam('limit', queryParams['limit'], {
    fallback: DEFAULT_PAGE_SIZE,
    max: MAX_PAGE_SIZE,
    min: 1,
  });
  const offset = readPageParam('offset', queryParams['offset'], {
    fallback: 0,
    min: 0,
  });
  if (typeof limit !== 'number' || typeof offset !== 'number') {
    const errors = [limit, offset].filter((value) => typeof value !== 'number');
    return new MirageResponse(422, {}, { detail: errors });
  }

  return {
    data: items.slice(offset, offset + limit),
    meta: { limit, offset, total: items.length },
  };
}

type SearchResults = OkBody<'/api/search'>['data'];
type SearchKind = keyof SearchResults;
type SearchCard<K extends SearchKind> = SearchResults[K][number];

/**
 * @description Each kind's fixture list, and the columns its list route's `q` matches
 * (`docs/plans/catalog-search.md` Q6).
 */
const searchKinds: {
  [K in SearchKind]: {
    columns: (card: SearchCard<K>) => readonly (Nullable<string> | undefined)[];
    items: readonly SearchCard<K>[];
  };
} = {
  characters: { columns: ({ name, slug }) => [slug, name], items: mockCharacters },
  mechanical_designers: {
    columns: ({ name, slug }) => [slug, name],
    items: mockMechanicalDesigners,
  },
  mobile_suits: {
    columns: ({ model_number, name, slug }) => [slug, name, model_number],
    items: mockMobileSuits,
  },
  organizations: {
    columns: ({ name, slug }) => [slug, name],
    items: mockOrganizations,
  },
  works: { columns: ({ slug, title }) => [slug, title], items: mockWorks },
};

const SEARCH_KINDS = Object.keys(searchKinds) as SearchKind[];

/** @description One kind's matches for `q`, prefix matches first, in its list order. */
function searchKind<K extends SearchKind>(
  kind: K,
  q: string | undefined,
): readonly SearchCard<K>[] {
  const { columns, items } = searchKinds[kind];
  return searchList({ columns, items, q });
}

/**
 * @description Answers `/api/search` as the API does (`docs/plans/catalog-search.md`):
 * the first `limit` matches of each kind, by `searchList`, with every kind's total. A
 * missing or blank `q` lists the first rows of each kind.
 * @returns A 422 `MirageResponse`, with the API's body, for a `limit` outside
 * `1..SEARCH_MAX_LIMIT` or a `q` longer than `MAX_SEARCH_LENGTH`.
 */
export function searchCatalog({
  queryParams,
}: Pick<Request, 'queryParams'>): OkBody<'/api/search'> | MirageResponse {
  const limit = readPageParam('limit', queryParams['limit'], {
    fallback: SEARCH_DEFAULT_LIMIT,
    max: SEARCH_MAX_LIMIT,
    min: 1,
  });
  const rawQ = queryParams['q'];
  const q = typeof rawQ === 'string' ? rawQ : undefined;
  const errors: ValidationError[] = typeof limit === 'number' ? [] : [limit];
  // NOTE: FastAPI counts code points, not UTF-16 units.
  if (q !== undefined && Array.from(q).length > MAX_SEARCH_LENGTH) {
    errors.push({
      loc: ['query', 'q'],
      msg: `String should have at most ${MAX_SEARCH_LENGTH} characters`,
      type: 'string_too_long',
    });
  }
  if (typeof limit !== 'number' || errors.length > 0) {
    return new MirageResponse(422, {}, { detail: errors });
  }

  const matches = SEARCH_KINDS.map((kind) => [kind, searchKind(kind, q)] as const);
  // NOTE: `Object.fromEntries` types its keys as `string`, so each result is asserted back
  // to its kinds. `SEARCH_KINDS` lists every kind, so no key is missing.
  return {
    data: Object.fromEntries(
      matches.map(([kind, cards]) => [kind, cards.slice(0, limit)]),
    ) as SearchResults,
    meta: {
      limit,
      totals: Object.fromEntries(
        matches.map(([kind, cards]) => [kind, cards.length]),
      ) as Record<SearchKind, number>,
    },
  };
}

/** @description The API's 404 for a detail path whose slug matches nothing. */
export function notFound(detail: string): MirageResponse {
  return new MirageResponse(404, {}, { detail });
}

/**
 * @description A detail route's handler: it finds the row by the path's slug, or
 * answers with the route's 404.
 */
function detailHandler<T>({
  find,
  notFoundDetail,
  param,
}: {
  find: (slug: string) => T | undefined;
  notFoundDetail: string;
  param: string;
}): (request: Request) => { data: T } | MirageResponse {
  return ({ params }) => {
    const found = find(params[param] ?? '');
    return found === undefined ? notFound(notFoundDetail) : { data: found };
  };
}

/**
 * @description A sub-list route's handler (`/{slug}/mobile-suits`): it finds the parent,
 * then pages its list. An unknown parent is the route's 404.
 * @note The parent is resolved first, so an old slug lists the renamed row's items (D2).
 */
function subListHandler<Parent, Item>({
  find,
  list,
  notFoundDetail,
  param,
}: {
  find: (slug: string) => Parent | undefined;
  list: (parent: Parent) => readonly Item[];
  notFoundDetail: string;
  param: string;
}): (request: Request) => { data: Item[]; meta: PageMeta } | MirageResponse {
  return (request) => {
    const parent = find(request.params[param] ?? '');
    return parent === undefined
      ? notFound(notFoundDetail)
      : paginate(list(parent), request);
  };
}

/**
 * @description Every route `makeMirageServer` answers, with its happy-path fixture.
 * Error responses belong in each test's `overrides`.
 */
export const endpointConfigs: readonly AnyEndpointConfig[] = [
  { path: '/api/characters', handler: (request) => paginate(mockCharacters, request) },
  {
    path: '/api/characters/{character_slug}',
    handler: detailHandler({
      find: findCharacterMock,
      notFoundDetail: 'Character not found',
      param: 'character_slug',
    }),
  },
  { path: '/api/continuities', handler: () => mockContinuitiesListResponse },
  { path: '/api/health-check', handler: () => mockHealthCheckResponse },
  {
    path: '/api/mechanical-designers',
    handler: (request) => paginate(mockMechanicalDesigners, request),
  },
  {
    path: '/api/mechanical-designers/{mechanical_designer_slug}',
    handler: detailHandler({
      find: findMechanicalDesignerMock,
      notFoundDetail: 'Mechanical designer not found',
      param: 'mechanical_designer_slug',
    }),
  },
  {
    path: '/api/mechanical-designers/{mechanical_designer_slug}/mobile-suits',
    handler: subListHandler({
      find: findMechanicalDesignerMock,
      list: ({ slug }) => findMechanicalDesignerMobileSuitsMock(slug),
      notFoundDetail: 'Mechanical designer not found',
      param: 'mechanical_designer_slug',
    }),
  },
  {
    path: '/api/mobile-suits',
    handler: (request) => paginate(mockMobileSuits, request),
  },
  {
    path: '/api/mobile-suits/{mobile_suit_slug}',
    handler: detailHandler({
      find: findMobileSuitMock,
      notFoundDetail: 'Mobile suit not found',
      param: 'mobile_suit_slug',
    }),
  },
  {
    path: '/api/organizations',
    handler: (request) => paginate(mockOrganizations, request),
  },
  {
    path: '/api/organizations/{organization_slug}',
    handler: detailHandler({
      find: findOrganizationMock,
      notFoundDetail: 'Organization not found',
      param: 'organization_slug',
    }),
  },
  {
    path: '/api/organizations/{organization_slug}/mobile-suits',
    handler: subListHandler({
      find: findOrganizationMock,
      list: ({ slug }) => findOrganizationMobileSuitsMock(slug),
      notFoundDetail: 'Organization not found',
      param: 'organization_slug',
    }),
  },
  { path: '/api/search', handler: searchCatalog },
  { path: '/api/works', handler: (request) => paginate(mockWorks, request) },
  {
    path: '/api/works/{work_slug}',
    handler: detailHandler({
      find: findWorkMock,
      notFoundDetail: 'Work not found',
      param: 'work_slug',
    }),
  },
  {
    path: '/api/works/{work_slug}/mobile-suits',
    handler: subListHandler({
      find: findWorkMock,
      list: ({ slug }) => findWorkMobileSuitsMock(slug),
      notFoundDetail: 'Work not found',
      param: 'work_slug',
    }),
  },
];
