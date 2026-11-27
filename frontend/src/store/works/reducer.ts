import {
  REQUEST_WORK,
  REQUEST_WORK_MOBILE_SUITS,
  REQUEST_WORKS,
  SET_WORK,
  SET_WORK_ERROR,
  SET_WORK_MOBILE_SUITS,
  SET_WORK_MOBILE_SUITS_ERROR,
  SET_WORKS,
  SET_WORKS_ERROR,
} from '@/store/actionTypes';
import {
  createInitialListState,
  requestDetail,
  requestList,
  requestSubList,
  setDetailError,
  setDetailUnderSlugs,
  setList,
  setListError,
} from '@/store/catalogList';
import { combineReducers } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

import type { CombinedWorksStateSlice, WorksStateSlice } from './reducer.types';

export const initialWorksStateSlice: WorksStateSlice = {
  detailsBySlug: {},
  list: createInitialListState(),
  mobileSuits: createInitialListState(),
};

const detailsBySlug: CombinedWorksStateSlice['detailsBySlug'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_WORK:
        return requestDetail(stateSlice, action.payload.works);
      case SET_WORK:
        return setDetailUnderSlugs(stateSlice, action.payload.works);
      case SET_WORK_ERROR:
        return setDetailError(stateSlice, action.payload.works);
      default:
        return stateSlice;
    }
  },
  initialWorksStateSlice.detailsBySlug,
];

const list: CombinedWorksStateSlice['list'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_WORKS:
        return requestList(stateSlice, action.payload.works);
      case SET_WORKS:
        return setList(stateSlice, action.payload.works);
      case SET_WORKS_ERROR:
        return setListError(stateSlice, action.payload.works);
      default:
        return stateSlice;
    }
  },
  initialWorksStateSlice.list,
];

const mobileSuits: CombinedWorksStateSlice['mobileSuits'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_WORK_MOBILE_SUITS:
        return requestSubList(stateSlice, action.payload.works);
      case SET_WORK_MOBILE_SUITS:
        return setList(stateSlice, action.payload.works);
      case SET_WORK_MOBILE_SUITS_ERROR:
        return setListError(stateSlice, action.payload.works);
      default:
        return stateSlice;
    }
  },
  initialWorksStateSlice.mobileSuits,
];

export default combineReducers<WorksStateSlice, AppAction>({
  detailsBySlug,
  list,
  mobileSuits,
});
