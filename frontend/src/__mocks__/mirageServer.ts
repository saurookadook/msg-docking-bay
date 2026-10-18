import { createServer, type Server } from 'miragejs';

import { BASE_API_URL } from '@/constants';

import { mockHealthCheckResponse } from './healthMocks';

/**
 * @description Replaces or adds routes on a server built by `makeMirageServer`. Paths
 * are relative to the `/api` namespace: `server.get('/health-check', ...)`.
 */
export type MirageRouteOverrides = (server: Server) => void;

/**
 * @description Starts a Mirage server that answers every API route the app calls with
 * the fixtures in `__mocks__/`. Tests and Storybook share it.
 * @note Call `server.shutdown()` when finished. In the `test` environment an unhandled
 * request throws; in `development` (Storybook) it passes through to the network.
 * @example
 * ```ts
 * const server = makeMirageServer({
 *   environment: 'test',
 *   overrides: (server) => {
 *     server.get('/health-check', () => new MirageResponse(503, {}, { detail: '...' }));
 *   },
 * });
 * ```
 */
export function makeMirageServer({
  environment = 'development', // force formatting
  overrides,
}: {
  environment?: 'development' | 'test';
  overrides?: MirageRouteOverrides;
} = {}): Server {
  return createServer({
    environment,
    routes() {
      this.urlPrefix = BASE_API_URL;
      this.namespace = 'api';

      this.get('/health-check', () => mockHealthCheckResponse);

      overrides?.(this);

      if (environment === 'development') {
        this.namespace = '';
        this.passthrough();
      }
    },
  });
}
