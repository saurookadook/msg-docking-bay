import { combineReducers } from './combineReducers';
import healthReducer, { initialHealthStateSlice } from './health/reducer';
import type { HealthStateSlice } from './health/reducer.types';
import type { AppAction } from './types';

export type AppState = {
  health: HealthStateSlice;
};

export const initialAppState: AppState = {
  health: initialHealthStateSlice,
};

export const appReducer = combineReducers<AppState, AppAction>({
  health: [healthReducer, initialAppState.health],
});
