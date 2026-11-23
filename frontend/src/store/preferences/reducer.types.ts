import type { SET_SHIFT } from '@/store/actionTypes';
import type { CombinedReducer } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';
import type { Shift } from '@/types';

export type PreferencesStateSlice = {
  shift: Shift;
};

export type PreferencesAction = {
  type: typeof SET_SHIFT;
  payload: { preferences: { shift: Shift } };
};

export type CombinedPreferencesStateSlice = CombinedReducer<
  PreferencesStateSlice,
  AppAction
>;
