import type { HealthCheckResponse } from '@/types';

export const mockHealthCheckResponse: HealthCheckResponse = {
  data: { status: 'ok' },
};

export const mockHealthCheckErrorDetail = 'The API is unavailable.';
