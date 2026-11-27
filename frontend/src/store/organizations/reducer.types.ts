import type { OrganizationCardEntity, OrganizationDetailEntity } from '@/api';
import type {
  REQUEST_ORGANIZATION,
  REQUEST_ORGANIZATIONS,
  SET_ORGANIZATION,
  SET_ORGANIZATION_ERROR,
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
};

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
    };

export type CombinedOrganizationsStateSlice = CombinedReducer<
  OrganizationsStateSlice,
  AppAction
>;
