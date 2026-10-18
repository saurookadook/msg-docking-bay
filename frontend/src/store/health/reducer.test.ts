import { describe, expect, it } from 'vitest';

import { mockHealthCheckResponse } from '@/__mocks__/healthMocks';
import {
  REQUEST_HEALTH_CHECK, // force formatting
  SET_HEALTH_CHECK,
  SET_HEALTH_CHECK_ERROR,
} from '@/store/actionTypes';

import healthReducer, { initialHealthStateSlice } from './reducer';

describe('healthReducer', () => {
  it('marks a request as in progress and clears the previous result', () => {
    const stateWithResult = {
      ...initialHealthStateSlice,
      healthCheck: mockHealthCheckResponse.data,
    };

    expect(healthReducer(stateWithResult, { type: REQUEST_HEALTH_CHECK })).toEqual({
      healthCheck: null,
      healthCheckErrorMessage: null,
      healthCheckRequestInProgress: true,
    });
  });

  it('stores the health check and ends the request', () => {
    const requestingState = {
      ...initialHealthStateSlice,
      healthCheckRequestInProgress: true,
    };

    expect(
      healthReducer(requestingState, {
        type: SET_HEALTH_CHECK,
        payload: { health: { healthCheck: mockHealthCheckResponse.data } },
      }),
    ).toEqual({
      healthCheck: mockHealthCheckResponse.data,
      healthCheckErrorMessage: null,
      healthCheckRequestInProgress: false,
    });
  });

  it('stores the error message and ends the request', () => {
    const requestingState = {
      ...initialHealthStateSlice,
      healthCheckRequestInProgress: true,
    };

    expect(
      healthReducer(requestingState, {
        type: SET_HEALTH_CHECK_ERROR,
        payload: { health: { errorMessage: 'Down' } },
      }),
    ).toEqual({
      healthCheck: null,
      healthCheckErrorMessage: 'Down',
      healthCheckRequestInProgress: false,
    });
  });
});
