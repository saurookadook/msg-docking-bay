import type { CharactersAction } from './characters/reducer.types';
import type { ContinuitiesAction } from './continuities/reducer.types';
import type { HealthAction } from './health/reducer.types';
import type { MechanicalDesignersAction } from './mechanical-designers/reducer.types';
import type { MobileSuitsAction } from './mobile-suits/reducer.types';
import type { OrganizationsAction } from './organizations/reducer.types';
import type { PreferencesAction } from './preferences/reducer.types';
import type { WorksAction } from './works/reducer.types';

/** @description Every action the app store handles: one union member per slice. */
export type AppAction =
  | CharactersAction
  | ContinuitiesAction
  | HealthAction
  | MechanicalDesignersAction
  | MobileSuitsAction
  | OrganizationsAction
  | PreferencesAction
  | WorksAction;

export type AppDispatch = React.Dispatch<AppAction>;

export type BaseAction = {
  dispatch: AppDispatch;
};
