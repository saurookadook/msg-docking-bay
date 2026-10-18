import type {
  REQUEST_HEALTH_CHECK, // force formatting
  SET_HEALTH_CHECK,
  SET_HEALTH_CHECK_ERROR,
} from '@/store/actionTypes';
import type { CombinedReducer } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';
import type { HealthCheck, Nullable } from '@/types';

export type HealthStateSlice = {
  healthCheck: Nullable<HealthCheck>;
  healthCheckErrorMessage: Nullable<string>;
  healthCheckRequestInProgress: boolean;
};

export type HealthAction =
  | { type: typeof REQUEST_HEALTH_CHECK }
  | { type: typeof SET_HEALTH_CHECK; payload: { health: { healthCheck: HealthCheck } } }
  | {
      type: typeof SET_HEALTH_CHECK_ERROR;
      payload: { health: { errorMessage: string } };
    };

export type CombinedHealthStateSlice = CombinedReducer<HealthStateSlice, AppAction>;
