import {
  REQUEST_ORGANIZATIONS, // force formatting
  SET_ORGANIZATIONS,
  SET_ORGANIZATIONS_ERROR,
} from '@/store/actionTypes';
import {
  createInitialListState,
  requestList,
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
  list: createInitialListState(),
};

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

export default combineReducers<OrganizationsStateSlice, AppAction>({
  list,
});
