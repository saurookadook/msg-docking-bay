export type FieldReducer<FieldState, Action> = (
  stateSlice: FieldState,
  action: Action,
) => FieldState;

/** @description A field's reducer paired with that field's initial value. */
export type FieldReducerEntry<FieldState, Action> = [
  FieldReducer<FieldState, Action>,
  FieldState,
];

export type CombinedReducer<State, Action> = {
  [Key in keyof State]: FieldReducerEntry<State[Key], Action>;
};

/**
 * @description Builds one reducer for a state object from one reducer per field.
 * @example
 * ```ts
 * export default combineReducers<HealthStateSlice, AppAction>({
 *   healthCheck,
 *   healthCheckErrorMessage,
 *   healthCheckRequestInProgress,
 * });
 * ```
 */
export function combineReducers<State extends object, Action>(
  combinedReducer: CombinedReducer<State, Action>,
): (state: State, action: Action) => State {
  const keys = Object.keys(combinedReducer) as (keyof State)[];

  return function reducer(state, action) {
    // NOTE: every key of `State` is assigned in the loop below.
    const nextState = {} as State;
    for (const key of keys) {
      const [fieldReducer] = combinedReducer[key];
      nextState[key] = fieldReducer(state[key], action);
    }
    return nextState;
  };
}
