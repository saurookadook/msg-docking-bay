import {
  REQUEST_MOBILE_SUITS, // force formatting
  SET_MOBILE_SUITS,
  SET_MOBILE_SUITS_ERROR,
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
  CombinedMobileSuitsStateSlice,
  MobileSuitsStateSlice,
} from './reducer.types';

export const initialMobileSuitsStateSlice: MobileSuitsStateSlice = {
  list: createInitialListState(),
};

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
  list,
});
