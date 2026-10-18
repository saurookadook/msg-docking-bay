import { Response as MirageResponse, type Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import {
  mockHealthCheckErrorDetail,
  mockHealthCheckResponse,
} from '@/__mocks__/healthMocks';
import { makeMirageServer } from '@/__mocks__/mirageServer';
import type { HealthCheckResponse } from '@/types';

import { safeFetch } from './safeFetch';

function callHealthCheck() {
  return safeFetch.call<HealthCheckResponse>(
    { name: 'safeFetch__tests' },
    { requestPathname: '/api/health-check', fetchOpts: { method: 'GET' } },
  );
}

describe('safeFetch', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  describe("'call' method", () => {
    it('returns the parsed body of a successful response', async () => {
      server = makeMirageServer({ environment: 'test' });

      await expect(callHealthCheck()).resolves.toEqual(mockHealthCheckResponse);
    });

    it("throws a tagged error carrying the status and the API's detail", async () => {
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirageServer) => {
          mirageServer.get(
            '/health-check',
            () => new MirageResponse(503, {}, { detail: mockHealthCheckErrorDetail }),
          );
        },
      });

      await expect(callHealthCheck()).rejects.toMatchObject({
        name: 'SafeFetchError',
        status: 503,
        detail: mockHealthCheckErrorDetail,
      });
    });

    it('throws when a successful response is not JSON', async () => {
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirageServer) => {
          mirageServer.get(
            '/health-check',
            () =>
              new MirageResponse(200, { 'Content-Type': 'text/html' }, '<html></html>'),
          );
        },
      });

      await expect(callHealthCheck()).rejects.toThrow('Expected a JSON body');
    });
  });
});
