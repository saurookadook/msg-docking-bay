import charactersReducer, { initialCharactersStateSlice } from './characters/reducer';
import type { CharactersStateSlice } from './characters/reducer.types';
import { combineReducers } from './combineReducers';
import continuitiesReducer, {
  initialContinuitiesStateSlice,
} from './continuities/reducer';
import type { ContinuitiesStateSlice } from './continuities/reducer.types';
import healthReducer, { initialHealthStateSlice } from './health/reducer';
import type { HealthStateSlice } from './health/reducer.types';
import mechanicalDesignersReducer, {
  initialMechanicalDesignersStateSlice,
} from './mechanical-designers/reducer';
import type { MechanicalDesignersStateSlice } from './mechanical-designers/reducer.types';
import mobileSuitsReducer, {
  initialMobileSuitsStateSlice,
} from './mobile-suits/reducer';
import type { MobileSuitsStateSlice } from './mobile-suits/reducer.types';
import organizationsReducer, {
  initialOrganizationsStateSlice,
} from './organizations/reducer';
import type { OrganizationsStateSlice } from './organizations/reducer.types';
import preferencesReducer, {
  initialPreferencesStateSlice,
} from './preferences/reducer';
import type { PreferencesStateSlice } from './preferences/reducer.types';
import type { AppAction } from './types';
import worksReducer, { initialWorksStateSlice } from './works/reducer';
import type { WorksStateSlice } from './works/reducer.types';

export type AppState = {
  characters: CharactersStateSlice;
  continuities: ContinuitiesStateSlice;
  health: HealthStateSlice;
  mechanicalDesigners: MechanicalDesignersStateSlice;
  mobileSuits: MobileSuitsStateSlice;
  organizations: OrganizationsStateSlice;
  preferences: PreferencesStateSlice;
  works: WorksStateSlice;
};

export const initialAppState: AppState = {
  characters: initialCharactersStateSlice,
  continuities: initialContinuitiesStateSlice,
  health: initialHealthStateSlice,
  mechanicalDesigners: initialMechanicalDesignersStateSlice,
  mobileSuits: initialMobileSuitsStateSlice,
  organizations: initialOrganizationsStateSlice,
  preferences: initialPreferencesStateSlice,
  works: initialWorksStateSlice,
};

export const appReducer = combineReducers<AppState, AppAction>({
  characters: [charactersReducer, initialAppState.characters],
  continuities: [continuitiesReducer, initialAppState.continuities],
  health: [healthReducer, initialAppState.health],
  mechanicalDesigners: [
    mechanicalDesignersReducer,
    initialAppState.mechanicalDesigners,
  ],
  mobileSuits: [mobileSuitsReducer, initialAppState.mobileSuits],
  organizations: [organizationsReducer, initialAppState.organizations],
  preferences: [preferencesReducer, initialAppState.preferences],
  works: [worksReducer, initialAppState.works],
});
