import { SET_SHIFT } from '@/store/actionTypes';
import { combineReducers } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

import type {
  CombinedPreferencesStateSlice,
  PreferencesStateSlice,
} from './reducer.types';

/**
 * @description `auto` until `hydrateShift` reads the stored shift after mount.
 * @note `index.html` has already applied the stored shift to the page by then, so the
 * colors never flash; only the toggle shows `auto` for that first render.
 */
export const initialPreferencesStateSlice: PreferencesStateSlice = {
  shift: 'auto',
};

const shift: CombinedPreferencesStateSlice['shift'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case SET_SHIFT:
        return action.payload.preferences.shift;
      default:
        return stateSlice;
    }
  },
  initialPreferencesStateSlice.shift,
];

export default combineReducers<PreferencesStateSlice, AppAction>({
  shift,
});
