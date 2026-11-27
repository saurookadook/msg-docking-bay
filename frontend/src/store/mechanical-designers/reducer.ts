import {
  REQUEST_MECHANICAL_DESIGNER,
  REQUEST_MECHANICAL_DESIGNER_MOBILE_SUITS,
  REQUEST_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNER,
  SET_MECHANICAL_DESIGNER_ERROR,
  SET_MECHANICAL_DESIGNER_MOBILE_SUITS,
  SET_MECHANICAL_DESIGNER_MOBILE_SUITS_ERROR,
  SET_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNERS_ERROR,
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
  CombinedMechanicalDesignersStateSlice,
  MechanicalDesignersStateSlice,
} from './reducer.types';

export const initialMechanicalDesignersStateSlice: MechanicalDesignersStateSlice = {
  detailsBySlug: {},
  list: createInitialListState(),
  mobileSuits: createInitialListState(),
};

const detailsBySlug: CombinedMechanicalDesignersStateSlice['detailsBySlug'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_MECHANICAL_DESIGNER:
        return requestDetail(stateSlice, action.payload.mechanicalDesigners);
      case SET_MECHANICAL_DESIGNER:
        return setDetailUnderSlugs(stateSlice, action.payload.mechanicalDesigners);
      case SET_MECHANICAL_DESIGNER_ERROR:
        return setDetailError(stateSlice, action.payload.mechanicalDesigners);
      default:
        return stateSlice;
    }
  },
  initialMechanicalDesignersStateSlice.detailsBySlug,
];

const list: CombinedMechanicalDesignersStateSlice['list'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_MECHANICAL_DESIGNERS:
        return requestList(stateSlice, action.payload.mechanicalDesigners);
      case SET_MECHANICAL_DESIGNERS:
        return setList(stateSlice, action.payload.mechanicalDesigners);
      case SET_MECHANICAL_DESIGNERS_ERROR:
        return setListError(stateSlice, action.payload.mechanicalDesigners);
      default:
        return stateSlice;
    }
  },
  initialMechanicalDesignersStateSlice.list,
];

const mobileSuits: CombinedMechanicalDesignersStateSlice['mobileSuits'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_MECHANICAL_DESIGNER_MOBILE_SUITS:
        return requestList(stateSlice, action.payload.mechanicalDesigners);
      case SET_MECHANICAL_DESIGNER_MOBILE_SUITS:
        return setList(stateSlice, action.payload.mechanicalDesigners);
      case SET_MECHANICAL_DESIGNER_MOBILE_SUITS_ERROR:
        return setListError(stateSlice, action.payload.mechanicalDesigners);
      default:
        return stateSlice;
    }
  },
  initialMechanicalDesignersStateSlice.mobileSuits,
];

export default combineReducers<MechanicalDesignersStateSlice, AppAction>({
  detailsBySlug,
  list,
  mobileSuits,
});
