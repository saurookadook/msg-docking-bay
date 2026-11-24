import {
  REQUEST_MECHANICAL_DESIGNERS, // force formatting
  SET_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNERS_ERROR,
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
  CombinedMechanicalDesignersStateSlice,
  MechanicalDesignersStateSlice,
} from './reducer.types';

export const initialMechanicalDesignersStateSlice: MechanicalDesignersStateSlice = {
  list: createInitialListState(),
};

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

export default combineReducers<MechanicalDesignersStateSlice, AppAction>({
  list,
});
