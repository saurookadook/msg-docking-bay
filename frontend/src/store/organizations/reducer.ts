import {
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
import {
  createInitialListState,
  requestDetail,
  requestList,
  setDetailError,
  setDetailUnderSlugs,
  setList,
  setListError,
} from '@/store/catalogList';
import { combineReducers } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

import type {
  CombinedOrganizationsStateSlice,
  OrganizationsStateSlice,
} from './reducer.types';

export const initialOrganizationsStateSlice: OrganizationsStateSlice = {
  detailsBySlug: {},
  list: createInitialListState(),
  mobileSuitsByRole: {
    manufacturer: createInitialListState(),
    operator: createInitialListState(),
    developer: createInitialListState(),
  },
};

const detailsBySlug: CombinedOrganizationsStateSlice['detailsBySlug'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_ORGANIZATION:
        return requestDetail(stateSlice, action.payload.organizations);
      case SET_ORGANIZATION:
        return setDetailUnderSlugs(stateSlice, action.payload.organizations);
      case SET_ORGANIZATION_ERROR:
        return setDetailError(stateSlice, action.payload.organizations);
      default:
        return stateSlice;
    }
  },
  initialOrganizationsStateSlice.detailsBySlug,
];

const list: CombinedOrganizationsStateSlice['list'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_ORGANIZATIONS:
        return requestList(stateSlice, action.payload.organizations);
      case SET_ORGANIZATIONS:
        return setList(stateSlice, action.payload.organizations);
      case SET_ORGANIZATIONS_ERROR:
        return setListError(stateSlice, action.payload.organizations);
      default:
        return stateSlice;
    }
  },
  initialOrganizationsStateSlice.list,
];

const mobileSuitsByRole: CombinedOrganizationsStateSlice['mobileSuitsByRole'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_ORGANIZATION_MOBILE_SUITS: {
        const { role, ...payload } = action.payload.organizations;
        return { ...stateSlice, [role]: requestList(stateSlice[role], payload) };
      }
      case SET_ORGANIZATION_MOBILE_SUITS: {
        const { role, ...payload } = action.payload.organizations;
        return { ...stateSlice, [role]: setList(stateSlice[role], payload) };
      }
      case SET_ORGANIZATION_MOBILE_SUITS_ERROR: {
        const { role, ...payload } = action.payload.organizations;
        return { ...stateSlice, [role]: setListError(stateSlice[role], payload) };
      }
      default:
        return stateSlice;
    }
  },
  initialOrganizationsStateSlice.mobileSuitsByRole,
];

export default combineReducers<OrganizationsStateSlice, AppAction>({
  detailsBySlug,
  list,
  mobileSuitsByRole,
});
