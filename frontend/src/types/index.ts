export type Nullable<T> = T | null;

// TODO: replace these hand-written API types with the aliases generated into `@app/shared`
// (MONO-13, MONO-15) once the backend and the shared workspace exist. Until then they
// mirror FAPI-3 (`GET /api/health-check`) inside the FAPI-12 `data` envelope.
export type HealthCheck = {
  status: 'ok';
};

export type HealthCheckResponse = {
  data: HealthCheck;
};
