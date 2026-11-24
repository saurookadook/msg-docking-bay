import type { MobileSuitCardEntity } from '@/api';
import type {
  REQUEST_MOBILE_SUITS, // force formatting
  SET_MOBILE_SUITS,
  SET_MOBILE_SUITS_ERROR,
} from '@/store/actionTypes';
import type {
  ListErrorPayload,
  ListRequestPayload,
  ListSetPayload,
  ListState,
} from '@/store/catalogList';
import type { CombinedReducer } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

export type MobileSuitsStateSlice = {
  list: ListState<MobileSuitCardEntity>;
};

export type MobileSuitsAction =
  | { type: typeof REQUEST_MOBILE_SUITS; payload: { mobileSuits: ListRequestPayload } }
  | {
      type: typeof SET_MOBILE_SUITS;
      payload: { mobileSuits: ListSetPayload<MobileSuitCardEntity> };
    }
  | { type: typeof SET_MOBILE_SUITS_ERROR; payload: { mobileSuits: ListErrorPayload } };

export type CombinedMobileSuitsStateSlice = CombinedReducer<
  MobileSuitsStateSlice,
  AppAction
>;
