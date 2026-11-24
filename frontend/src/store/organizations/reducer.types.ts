import type { OrganizationCardEntity } from '@/api';
import type {
  REQUEST_ORGANIZATIONS, // force formatting
  SET_ORGANIZATIONS,
  SET_ORGANIZATIONS_ERROR,
} from '@/store/actionTypes';
import type {
  ListErrorPayload,
  ListRequestPayload,
  ListSetPayload,
  ListState,
} from '@/store/catalogList';
import type { CombinedReducer } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

export type OrganizationsStateSlice = {
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
    };

export type CombinedOrganizationsStateSlice = CombinedReducer<
  OrganizationsStateSlice,
  AppAction
>;
