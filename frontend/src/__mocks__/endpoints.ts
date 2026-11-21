import { Response as MirageResponse, type Request } from 'miragejs';

import type { PageMeta, paths, ValidationError } from '@/api';
import { DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE } from '@/constants';

import { mockContinuitiesListResponse } from './continuityMocks';
import { mockHealthCheckResponse } from './healthMocks';
import {
  findMobileSuitMock,
  findWorkMobileSuitsMock,
  mockMobileSuits,
} from './mobileSuitMocks';
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

/** @description The API's 404 for a detail path whose slug matches nothing. */
export function notFound(detail: string): MirageResponse {
  return new MirageResponse(404, {}, { detail });
}

/**
 * @description Every route `makeMirageServer` answers, with its happy-path fixture.
 * Error responses belong in each test's `overrides`.
 */
export const endpointConfigs: readonly AnyEndpointConfig[] = [
  { path: '/api/continuities', handler: () => mockContinuitiesListResponse },
  { path: '/api/health-check', handler: () => mockHealthCheckResponse },
  {
    path: '/api/mobile-suits',
    handler: (request) => paginate(mockMobileSuits, request),
  },
  {
    path: '/api/mobile-suits/{mobile_suit_slug}',
    handler: ({ params }) => {
      const mobileSuit = findMobileSuitMock(params['mobile_suit_slug'] ?? '');
      return mobileSuit === undefined
        ? notFound('Mobile suit not found')
        : { data: mobileSuit };
    },
  },
  { path: '/api/works', handler: (request) => paginate(mockWorks, request) },
  {
    path: '/api/works/{work_slug}',
    handler: ({ params }) => {
      const work = findWorkMock(params['work_slug'] ?? '');
      return work === undefined ? notFound('Work not found') : { data: work };
    },
  },
  {
    path: '/api/works/{work_slug}/mobile-suits',
    handler: (request) => {
      // Resolved first, so an old slug lists the renamed work's suits (D2).
      const work = findWorkMock(request.params['work_slug'] ?? '');
      return work === undefined
        ? notFound('Work not found')
        : paginate(findWorkMobileSuitsMock(work.slug), request);
    },
  },
];
