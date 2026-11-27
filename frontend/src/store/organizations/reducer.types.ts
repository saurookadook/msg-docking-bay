import type {
  MobileSuitOrganizationRole,
  OrganizationCardEntity,
  OrganizationDetailEntity,
  OrganizationMobileSuitEntity,
} from '@/api';
import type {
  REQUEST_ORGANIZATION,
  REQUEST_ORGANIZATION_MOBILE_SUITS,
  REQUEST_ORGANIZATIONS,
  SET_ORGANIZATION,
  SET_ORGANIZATION_ERROR,
  SET_ORGANIZATION_MOBILE_SUITS,
  SET_ORGANIZATION_MOBILE_SUITS_ERROR,
  SET_ORGANIZATIONS,
  SET_ORGANIZATIONS_ERROR,
} from '@/store/actionTypes';
import type {
  DetailErrorPayload,
  DetailRequestPayload,
  DetailsBySlug,
  DetailSetPayload,
  ListErrorPayload,
  ListRequestPayload,
  ListSetPayload,
  ListState,
} from '@/store/catalogList';
import type { CombinedReducer } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

export type OrganizationsStateSlice = {
  detailsBySlug: DetailsBySlug<OrganizationDetailEntity>;
  list: ListState<OrganizationCardEntity>;
  /** @description Each role section's page of suits last asked for (`subListKey`). */
  mobileSuitsByRole: Record<
    MobileSuitOrganizationRole,
    ListState<OrganizationMobileSuitEntity>
  >;
};

/** @description A role section's list payload: which section, then the list's own payload. */
type RolePayload<Payload> = Payload & { role: MobileSuitOrganizationRole };

export type OrganizationsAction =
  | {
      type: typeof REQUEST_ORGANIZATIONS;
      payload: { organizations: ListRequestPayload };
    }
  | {
      type: typeof SET_ORGANIZATIONS;
      payload: { organizations: ListSetPayload<OrganizationCardEntity> };
    }
  | {
      type: typeof SET_ORGANIZATIONS_ERROR;
      payload: { organizations: ListErrorPayload };
    }
  | {
      type: typeof REQUEST_ORGANIZATION;
      payload: { organizations: DetailRequestPayload };
    }
  | {
      type: typeof SET_ORGANIZATION;
      payload: { organizations: DetailSetPayload<OrganizationDetailEntity> };
    }
  | {
      type: typeof SET_ORGANIZATION_ERROR;
      payload: { organizations: DetailErrorPayload };
    }
  | {
      type: typeof REQUEST_ORGANIZATION_MOBILE_SUITS;
      payload: { organizations: RolePayload<ListRequestPayload> };
    }
  | {
      type: typeof SET_ORGANIZATION_MOBILE_SUITS;
      payload: {
        organizations: RolePayload<ListSetPayload<OrganizationMobileSuitEntity>>;
      };
    }
  | {
      type: typeof SET_ORGANIZATION_MOBILE_SUITS_ERROR;
      payload: { organizations: RolePayload<ListErrorPayload> };
    };

export type CombinedOrganizationsStateSlice = CombinedReducer<
  OrganizationsStateSlice,
  AppAction
>;
