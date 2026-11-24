import type { ContinuityCardEntity } from '@/api';
import type {
  REQUEST_CONTINUITIES, // force formatting
  SET_CONTINUITIES,
  SET_CONTINUITIES_ERROR,
} from '@/store/actionTypes';
import type { CombinedReducer } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';
import type { Nullable } from '@/types';

/** @description Every continuity: `/api/continuities` is not paged, so it loads once. */
export type ContinuitiesStateSlice = {
  continuities: ContinuityCardEntity[];
  continuitiesErrorMessage: Nullable<string>;
  continuitiesRequestInProgress: boolean;
};

export type ContinuitiesAction =
  | { type: typeof REQUEST_CONTINUITIES }
  | {
      type: typeof SET_CONTINUITIES;
      payload: { continuities: { continuities: ContinuityCardEntity[] } };
    }
  | {
      type: typeof SET_CONTINUITIES_ERROR;
      payload: { continuities: { errorMessage: string } };
    };

export type CombinedContinuitiesStateSlice = CombinedReducer<
  ContinuitiesStateSlice,
  AppAction
>;
