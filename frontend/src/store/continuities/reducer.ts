import {
  REQUEST_CONTINUITIES, // force formatting
  SET_CONTINUITIES,
  SET_CONTINUITIES_ERROR,
} from '@/store/actionTypes';
import { combineReducers } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

import type {
  CombinedContinuitiesStateSlice,
  ContinuitiesStateSlice,
} from './reducer.types';

export const initialContinuitiesStateSlice: ContinuitiesStateSlice = {
  continuities: [],
  continuitiesErrorMessage: null,
  continuitiesRequestInProgress: false,
};

const continuities: CombinedContinuitiesStateSlice['continuities'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case SET_CONTINUITIES:
        return [...action.payload.continuities.continuities];
      default:
        return stateSlice;
    }
  },
  initialContinuitiesStateSlice.continuities,
];

const continuitiesErrorMessage: CombinedContinuitiesStateSlice['continuitiesErrorMessage'] =
  [
    (stateSlice, action) => {
      switch (action.type) {
        case REQUEST_CONTINUITIES:
        case SET_CONTINUITIES:
          return null;
        case SET_CONTINUITIES_ERROR:
          return action.payload.continuities.errorMessage;
        default:
          return stateSlice;
      }
    },
    initialContinuitiesStateSlice.continuitiesErrorMessage,
  ];

const continuitiesRequestInProgress: CombinedContinuitiesStateSlice['continuitiesRequestInProgress'] =
  [
    (stateSlice, action) => {
      switch (action.type) {
        case REQUEST_CONTINUITIES:
          return true;
        case SET_CONTINUITIES:
        case SET_CONTINUITIES_ERROR:
          return false;
        default:
          return stateSlice;
      }
    },
    initialContinuitiesStateSlice.continuitiesRequestInProgress,
  ];

export default combineReducers<ContinuitiesStateSlice, AppAction>({
  continuities,
  continuitiesErrorMessage,
  continuitiesRequestInProgress,
});
