import { Response as MirageResponse, type Server } from 'miragejs';
import { afterAll, afterEach, describe, expect, it, vi } from 'vitest';

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

  afterAll(() => {
    vi.restoreAllMocks();
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

    it('throws with the original as cause when the body cannot be read', async () => {
      /* START TEST SETUP */
      server = makeMirageServer({ environment: 'test' });
      const bodyReadError = new TypeError('terminated');
      // NOTE: Mirage cannot fail a body partway through, and its `Response` polyfill does
      // not read streams, so this one response rejects when its body is read.
      const unreadableResponse = new Response('{}');
      vi.spyOn(unreadableResponse, 'text').mockRejectedValueOnce(bodyReadError);
      vi.spyOn(window, 'fetch').mockResolvedValueOnce(unreadableResponse);
      /* END TEST SETUP */

      const callError: unknown = await callHealthCheck().catch(
        (error: unknown) => error,
      );

      expect(callError).toBeInstanceOf(Error);
      expect(callError).toMatchObject({
        message: expect.stringContaining("ERROR reading '/api/health-check'"),
        cause: bodyReadError,
      });
    });
  });
});
