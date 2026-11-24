import {
  REQUEST_MOBILE_SUIT,
  REQUEST_MOBILE_SUITS,
  SET_MOBILE_SUIT,
  SET_MOBILE_SUIT_ERROR,
  SET_MOBILE_SUITS,
  SET_MOBILE_SUITS_ERROR,
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
  CombinedMobileSuitsStateSlice,
  MobileSuitsStateSlice,
} from './reducer.types';

export const initialMobileSuitsStateSlice: MobileSuitsStateSlice = {
  detailsBySlug: {},
  list: createInitialListState(),
};

const detailsBySlug: CombinedMobileSuitsStateSlice['detailsBySlug'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_MOBILE_SUIT:
        return requestDetail(stateSlice, action.payload.mobileSuits);
      case SET_MOBILE_SUIT:
        return setDetailUnderSlugs(stateSlice, action.payload.mobileSuits);
      case SET_MOBILE_SUIT_ERROR:
        return setDetailError(stateSlice, action.payload.mobileSuits);
      default:
        return stateSlice;
    }
  },
  initialMobileSuitsStateSlice.detailsBySlug,
];

const list: CombinedMobileSuitsStateSlice['list'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_MOBILE_SUITS:
        return requestList(stateSlice, action.payload.mobileSuits);
      case SET_MOBILE_SUITS:
        return setList(stateSlice, action.payload.mobileSuits);
      case SET_MOBILE_SUITS_ERROR:
        return setListError(stateSlice, action.payload.mobileSuits);
      default:
        return stateSlice;
    }
  },
  initialMobileSuitsStateSlice.list,
];

export default combineReducers<MobileSuitsStateSlice, AppAction>({
  detailsBySlug,
  list,
});
