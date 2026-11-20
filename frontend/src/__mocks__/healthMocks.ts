import type { HealthCheckResponse } from '@/api';

export const mockHealthCheckResponse: HealthCheckResponse = {
  data: { status: 'ok' },
};

export const mockHealthCheckErrorDetail = 'The API is unavailable.';
