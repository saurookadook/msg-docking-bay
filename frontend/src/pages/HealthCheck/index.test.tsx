import { screen, within } from '@testing-library/react';
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
