import {
  REQUEST_HEALTH_CHECK, // force formatting
  SET_HEALTH_CHECK,
  SET_HEALTH_CHECK_ERROR,
} from '@/store/actionTypes';
import { combineReducers } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

import type { CombinedHealthStateSlice, HealthStateSlice } from './reducer.types';

export const initialHealthStateSlice: HealthStateSlice = {
  healthCheck: null,
  healthCheckErrorMessage: null,
  healthCheckRequestInProgress: false,
};

const healthCheck: CombinedHealthStateSlice['healthCheck'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_HEALTH_CHECK:
      case SET_HEALTH_CHECK_ERROR:
        return null;
      case SET_HEALTH_CHECK:
        return { ...action.payload.health.healthCheck };
      default:
        return stateSlice;
    }
  },
  initialHealthStateSlice.healthCheck,
];

const healthCheckErrorMessage: CombinedHealthStateSlice['healthCheckErrorMessage'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_HEALTH_CHECK:
      case SET_HEALTH_CHECK:
        return null;
      case SET_HEALTH_CHECK_ERROR:
        return action.payload.health.errorMessage;
      default:
        return stateSlice;
    }
  },
  initialHealthStateSlice.healthCheckErrorMessage,
];

const healthCheckRequestInProgress: CombinedHealthStateSlice['healthCheckRequestInProgress'] =
  [
    (stateSlice, action) => {
      switch (action.type) {
        case REQUEST_HEALTH_CHECK:
          return true;
        case SET_HEALTH_CHECK:
        case SET_HEALTH_CHECK_ERROR:
          return false;
        default:
          return stateSlice;
      }
    },
    initialHealthStateSlice.healthCheckRequestInProgress,
  ];

export default combineReducers<HealthStateSlice, AppAction>({
  healthCheck,
  healthCheckErrorMessage,
  healthCheckRequestInProgress,
});
