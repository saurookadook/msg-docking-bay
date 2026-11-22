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

// Characters.
export type CharacterCardEntity = Schemas['CharacterCardEntity'];
export type CharacterDetailEntity = Schemas['CharacterDetailEntity'];
export type CharacterRefEntity = Schemas['CharacterRefEntity'];
export type CharacterResponse = Schemas['CharacterResponse'];
export type CharactersListResponse = Schemas['CharactersListResponse'];
export type CitedWorkEntity = Schemas['CitedWorkEntity'];
export type PilotedMobileSuitEntity = Schemas['PilotedMobileSuitEntity'];

// Organizations.
export type MobileSuitOrganizationRole = Schemas['MobileSuitOrganizationRole'];
export type OrganizationCardEntity = Schemas['OrganizationCardEntity'];
export type OrganizationDetailEntity = Schemas['OrganizationDetailEntity'];
export type OrganizationLinkEntity = Schemas['OrganizationLinkEntity'];
export type OrganizationMobileSuitEntity = Schemas['OrganizationMobileSuitEntity'];
export type OrganizationMobileSuitsListResponse =
  Schemas['OrganizationMobileSuitsListResponse'];
export type OrganizationRefEntity = Schemas['OrganizationRefEntity'];
export type OrganizationResponse = Schemas['OrganizationResponse'];
export type OrganizationsListResponse = Schemas['OrganizationsListResponse'];

// Mechanical designers.
export type DesignedMobileSuitEntity = Schemas['DesignedMobileSuitEntity'];
export type MechanicalDesignerCardEntity = Schemas['MechanicalDesignerCardEntity'];
export type MechanicalDesignerDetailEntity = Schemas['MechanicalDesignerDetailEntity'];
export type MechanicalDesignerMobileSuitsListResponse =
  Schemas['MechanicalDesignerMobileSuitsListResponse'];
export type MechanicalDesignerRefEntity = Schemas['MechanicalDesignerRefEntity'];
export type MechanicalDesignerResponse = Schemas['MechanicalDesignerResponse'];
export type MechanicalDesignersListResponse =
  Schemas['MechanicalDesignersListResponse'];

// Mobile suits.
export type DesignerCreditEntity = Schemas['DesignerCreditEntity'];
export type OrganizationCreditEntity = Schemas['OrganizationCreditEntity'];
export type PilotCreditEntity = Schemas['PilotCreditEntity'];
export type MobileSuitAppearanceCardEntity = Schemas['MobileSuitAppearanceCardEntity'];
export type MobileSuitCardEntity = Schemas['MobileSuitCardEntity'];
export type MobileSuitDetailEntity = Schemas['MobileSuitDetailEntity'];
export type MobileSuitRelationType = Schemas['MobileSuitRelationType'];
export type MobileSuitResponse = Schemas['MobileSuitResponse'];
export type MobileSuitSpecSheetEntity = Schemas['MobileSuitSpecSheetEntity'];
export type MobileSuitsListResponse = Schemas['MobileSuitsListResponse'];
export type RelatedMobileSuitEntity = Schemas['RelatedMobileSuitEntity'];
export type UnitType = Schemas['UnitType'];
// NOTE: the backend's `SpecSheetField` Literal is inlined in the schema, not named.
export type SpecSheetField = MobileSuitSpecSheetEntity['inherited_fields'][number];

// Spec sheet parts.
export type ArmamentListingEntity = Schemas['ArmamentListingEntity'];
export type ArmamentMount = Schemas['ArmamentMount'];
export type ArmamentRefEntity = Schemas['ArmamentRefEntity'];
export type EquipmentFit = Schemas['EquipmentFit'];
export type EquipmentListingEntity = Schemas['EquipmentListingEntity'];
export type EquipmentRefEntity = Schemas['EquipmentRefEntity'];
export type MaterialListingEntity = Schemas['MaterialListingEntity'];
export type MaterialRefEntity = Schemas['MaterialRefEntity'];
export type MaterialUse = Schemas['MaterialUse'];
export type PowerplantListingEntity = Schemas['PowerplantListingEntity'];
export type PowerplantRefEntity = Schemas['PowerplantRefEntity'];
// NOTE: the backend's `SpecSheetPartKind` Literal is inlined too.
export type SpecSheetPartKind = MobileSuitSpecSheetEntity['inherited_parts'][number];
