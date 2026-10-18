import type { HealthAction } from './health/reducer.types';

/** @description Every action the app store handles: one union member per slice. */
export type AppAction = HealthAction;

export type AppDispatch = React.Dispatch<AppAction>;

export type BaseAction = {
  dispatch: AppDispatch;
};
