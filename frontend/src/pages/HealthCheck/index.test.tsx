import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Response as MirageResponse, type Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import {
  mockHealthCheckErrorDetail,
  mockHealthCheckResponse,
} from '@/__mocks__/healthMocks';
import { makeMirageServer } from '@/__mocks__/mirageServer';
import { renderWithProviders } from '@/utils/testing';

async function findHealthCheckSection() {
  return screen.findByRole('region', { name: 'Health Check' });
}

describe('HealthCheck', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  describe('when the API is healthy', () => {
    it('renders the API status', async () => {
      server = makeMirageServer({ environment: 'test' });
      renderWithProviders({ initialEntries: ['/health-check'] });

      const healthCheckSection = await findHealthCheckSection();
      expect(
        await within(healthCheckSection).findByRole('definition'),
      ).toHaveTextContent(mockHealthCheckResponse.data.status);
      expect(within(healthCheckSection).queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('when the request is in progress', () => {
    it('renders a loading status', async () => {
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirageServer) => {
          mirageServer.get('/health-check', () => mockHealthCheckResponse, {
            timing: 60_000,
          });
        },
      });
      renderWithProviders({ initialEntries: ['/health-check'] });

      const healthCheckSection = await findHealthCheckSection();
      expect(await within(healthCheckSection).findByRole('status')).toHaveTextContent(
        'Checking API health',
      );
      expect(
        within(healthCheckSection).queryByRole('definition'),
      ).not.toBeInTheDocument();
    });
  });

  describe('when the page is left and reopened while a request is in progress', () => {
    it("ignores the earlier request's late result", async () => {
      /* START TEST SETUP */
      // NOTE: Mirage awaits a handler's returned promise, so the first request stays
      // pending until the test releases it, after the second request has finished.
      let releaseStaleRequest = () => {};
      const staleRequestReleased = new Promise<void>((resolve) => {
        releaseStaleRequest = resolve;
      });
      let requestCount = 0;
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirageServer) => {
          mirageServer.get('/health-check', async () => {
            requestCount += 1;
            if (requestCount > 1) {
              return mockHealthCheckResponse;
            }
            await staleRequestReleased;
            return new MirageResponse(503, {}, { detail: mockHealthCheckErrorDetail });
          });
        },
      });
      const user = userEvent.setup();
      renderWithProviders({ initialEntries: ['/health-check'] });
      await within(await findHealthCheckSection()).findByRole('status');
      /* END TEST SETUP */

      await user.click(screen.getByRole('link', { name: 'Home' }));
      await user.click(screen.getByRole('link', { name: 'Health check' }));

      const healthCheckSection = await findHealthCheckSection();
      expect(
        await within(healthCheckSection).findByRole('definition'),
      ).toHaveTextContent(mockHealthCheckResponse.data.status);

      releaseStaleRequest();

      await expect(
        within(healthCheckSection).findByRole('alert', {}, { timeout: 250 }),
      ).rejects.toThrow();
      expect(within(healthCheckSection).getByRole('definition')).toHaveTextContent(
        mockHealthCheckResponse.data.status,
      );
    });
  });

  describe('when the API returns an error', () => {
    it("renders the API's error detail", async () => {
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirageServer) => {
          mirageServer.get(
            '/health-check',
            () => new MirageResponse(503, {}, { detail: mockHealthCheckErrorDetail }),
          );
        },
      });
      renderWithProviders({ initialEntries: ['/health-check'] });

      const healthCheckSection = await findHealthCheckSection();
      expect(await within(healthCheckSection).findByRole('alert')).toHaveTextContent(
        mockHealthCheckErrorDetail,
      );
      expect(within(healthCheckSection).queryByRole('status')).not.toBeInTheDocument();
    });
  });
});
