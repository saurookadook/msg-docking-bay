import { describe, expect, it } from 'vitest';

import { SET_SHIFT } from '@/store/actionTypes';

import preferencesReducer, { initialPreferencesStateSlice } from './reducer';

describe('preferencesReducer', () => {
  it('starts on the auto shift', () => {
    expect(initialPreferencesStateSlice).toEqual({ shift: 'auto' });
  });

  it('records the shift it is given', () => {
    expect(
      preferencesReducer(initialPreferencesStateSlice, {
        type: SET_SHIFT,
        payload: { preferences: { shift: 'night' } },
      }),
    ).toEqual({ shift: 'night' });
  });
});
