import { combineReducers } from './combineReducers';
import healthReducer, { initialHealthStateSlice } from './health/reducer';
import type { HealthStateSlice } from './health/reducer.types';
import preferencesReducer, {
  initialPreferencesStateSlice,
} from './preferences/reducer';
import type { PreferencesStateSlice } from './preferences/reducer.types';
import type { AppAction } from './types';

export type AppState = {
  health: HealthStateSlice;
  preferences: PreferencesStateSlice;
};

export const initialAppState: AppState = {
  health: initialHealthStateSlice,
  preferences: initialPreferencesStateSlice,
};

export const appReducer = combineReducers<AppState, AppAction>({
  health: [healthReducer, initialAppState.health],
  preferences: [preferencesReducer, initialAppState.preferences],
});
