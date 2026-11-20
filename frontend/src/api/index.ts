// Names for the API's types, generated from the backend's OpenAPI schema into `./generated`
// (MONO-13, MONO-15). Each alias keeps its backend model's name. Run `pnpm run api:generate`
// after changing the backend's API, and import these from `@/api`, never from `./generated`.
import type { components } from './generated/api';

// Every route's operations, keyed by its OpenAPI path. The Mirage endpoint table checks its
// configs against it.
export type { paths } from './generated/api';

type Schemas = components['schemas'];

export type HealthCheckStatus = Schemas['HealthCheckStatus'];
export type HealthCheckResponse = Schemas['HealthCheckResponse'];
