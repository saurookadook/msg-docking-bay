import type { MobileSuitCardEntity, MobileSuitDetailEntity } from '@/api';
import type {
  REQUEST_MOBILE_SUIT,
  REQUEST_MOBILE_SUITS,
  SET_MOBILE_SUIT,
  SET_MOBILE_SUIT_ERROR,
  SET_MOBILE_SUITS,
  SET_MOBILE_SUITS_ERROR,
} from '@/store/actionTypes';
import type {
  DetailErrorPayload,
  DetailRequestPayload,
  DetailsBySlug,
  DetailSetPayload,
  ListErrorPayload,
  ListRequestPayload,
  ListSetPayload,
  ListState,
} from '@/store/catalogList';
import type { CombinedReducer } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

export type MobileSuitsStateSlice = {
  detailsBySlug: DetailsBySlug<MobileSuitDetailEntity>;
  list: ListState<MobileSuitCardEntity>;
};

export type MobileSuitsAction =
  | { type: typeof REQUEST_MOBILE_SUITS; payload: { mobileSuits: ListRequestPayload } }
  | {
      type: typeof SET_MOBILE_SUITS;
      payload: { mobileSuits: ListSetPayload<MobileSuitCardEntity> };
    }
  | { type: typeof SET_MOBILE_SUITS_ERROR; payload: { mobileSuits: ListErrorPayload } }
  | { type: typeof REQUEST_MOBILE_SUIT; payload: { mobileSuits: DetailRequestPayload } }
  | {
      type: typeof SET_MOBILE_SUIT;
      payload: { mobileSuits: DetailSetPayload<MobileSuitDetailEntity> };
    }
  | {
      type: typeof SET_MOBILE_SUIT_ERROR;
      payload: { mobileSuits: DetailErrorPayload };
    };

export type CombinedMobileSuitsStateSlice = CombinedReducer<
  MobileSuitsStateSlice,
  AppAction
>;
