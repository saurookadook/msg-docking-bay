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

// Shared pieces.
export type ContentLicense = Schemas['ContentLicense'];
export type PageMeta = Schemas['PageMeta'];
export type RelationDirection = Schemas['RelationDirection'];
export type SourceCitationEntity = Schemas['SourceCitationEntity'];
export type SourceKind = Schemas['SourceKind'];
export type ValidationError = Schemas['ValidationError'];

// Continuities.
export type ContinuitiesListResponse = Schemas['ContinuitiesListResponse'];
export type ContinuityCardEntity = Schemas['ContinuityCardEntity'];
export type ContinuityRefEntity = Schemas['ContinuityRefEntity'];

// Works.
export type RelatedWorkEntity = Schemas['RelatedWorkEntity'];
export type WorkAppearanceEntity = Schemas['WorkAppearanceEntity'];
export type WorkCardEntity = Schemas['WorkCardEntity'];
export type WorkDetailEntity = Schemas['WorkDetailEntity'];
export type WorkMobileSuitsListResponse = Schemas['WorkMobileSuitsListResponse'];
export type WorkRefEntity = Schemas['WorkRefEntity'];
export type WorkRelationType = Schemas['WorkRelationType'];
export type WorkResponse = Schemas['WorkResponse'];
export type WorkType = Schemas['WorkType'];
export type WorksListResponse = Schemas['WorksListResponse'];

// Mobile suits.
export type MobileSuitAppearanceCardEntity = Schemas['MobileSuitAppearanceCardEntity'];
export type MobileSuitCardEntity = Schemas['MobileSuitCardEntity'];
export type MobileSuitDetailEntity = Schemas['MobileSuitDetailEntity'];
export type MobileSuitRelationType = Schemas['MobileSuitRelationType'];
export type MobileSuitResponse = Schemas['MobileSuitResponse'];
export type MobileSuitSpecSheetEntity = Schemas['MobileSuitSpecSheetEntity'];
export type MobileSuitsListResponse = Schemas['MobileSuitsListResponse'];
export type RelatedMobileSuitEntity = Schemas['RelatedMobileSuitEntity'];
export type UnitType = Schemas['UnitType'];
// The backend's `SpecSheetField` Literal is inlined in the schema rather than named.
export type SpecSheetField = MobileSuitSpecSheetEntity['inherited_fields'][number];
