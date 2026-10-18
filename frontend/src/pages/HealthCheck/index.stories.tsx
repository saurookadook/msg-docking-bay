import type { Meta, StoryObj } from '@storybook/react-vite';
import { Response as MirageResponse, type Server } from 'miragejs';

import {
  mockHealthCheckErrorDetail,
  mockHealthCheckResponse,
} from '@/__mocks__/healthMocks';

import { HealthCheck } from '.';

const meta = {
  title: 'Pages/HealthCheck',
  component: HealthCheck,
  parameters: { route: '/health-check' },
} satisfies Meta<typeof HealthCheck>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Healthy: Story = {};

export const Loading: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get('/health-check', () => mockHealthCheckResponse, {
        timing: 60 * 60_000,
      });
    },
  },
};

export const Unhealthy: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/health-check',
        () => new MirageResponse(503, {}, { detail: mockHealthCheckErrorDetail }),
      );
    },
  },
};
