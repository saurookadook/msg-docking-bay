import type { Request } from 'miragejs';

import type { paths } from '@/api';

import { mockHealthCheckResponse } from './healthMocks';

/** @description The API's paths that have a `GET` operation. */
export type ApiGetPath = {
  [P in keyof paths]: paths[P] extends { get: object } ? P : never;
}[keyof paths];

/** @description The JSON body of a `GET` to `P` that succeeds with a 200. */
export type OkBody<P extends ApiGetPath> =
  paths[P]['get']['responses'][200]['content']['application/json'];

/**
 * @description One mocked route: an OpenAPI path from the generated contract, and a
 * handler that returns that path's 200 body.
 */
export type EndpointConfig<P extends ApiGetPath> = {
  path: P;
  handler: (request: Request) => OkBody<P>;
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

const DEFAULT_PAGE_LIMIT = 50;
const DEFAULT_PAGE_OFFSET = 0;

function readNonNegativeInt(
  value: Request['queryParams'][string],
  fallback: number,
): number {
  const parsed = typeof value === 'string' ? Number(value) : Number.NaN;
  return Number.isInteger(parsed) && parsed >= 0 ? parsed : fallback;
}

/**
 * @description Pages a list fixture the way the API does (D3 in
 * `docs/plans/catalog-read-api.md`): it reads `limit` and `offset` from the query, and
 * returns that page with its `meta`. An offset past the end gives an empty `data`.
 */
export function paginate<T>(
  items: readonly T[],
  { queryParams }: Pick<Request, 'queryParams'>,
): { data: T[]; meta: { limit: number; offset: number; total: number } } {
  const limit = readNonNegativeInt(queryParams['limit'], DEFAULT_PAGE_LIMIT);
  const offset = readNonNegativeInt(queryParams['offset'], DEFAULT_PAGE_OFFSET);

  return {
    data: items.slice(offset, offset + limit),
    meta: { limit, offset, total: items.length },
  };
}

/**
 * @description Every route `makeMirageServer` answers, with its happy-path fixture.
 * Error responses belong in each test's `overrides`.
 */
export const endpointConfigs: readonly AnyEndpointConfig[] = [
  { path: '/api/health-check', handler: () => mockHealthCheckResponse },
];
