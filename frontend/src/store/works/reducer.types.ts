import type {
  MobileSuitAppearanceCardEntity,
  WorkCardEntity,
  WorkDetailEntity,
} from '@/api';
import type {
  REQUEST_WORK,
  REQUEST_WORK_MOBILE_SUITS,
  REQUEST_WORKS,
  SET_WORK,
  SET_WORK_ERROR,
  SET_WORK_MOBILE_SUITS,
  SET_WORK_MOBILE_SUITS_ERROR,
  SET_WORKS,
  SET_WORKS_ERROR,
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

export type WorksStateSlice = {
  detailsBySlug: DetailsBySlug<WorkDetailEntity>;
  list: ListState<WorkCardEntity>;
  /** @description The page of the work's suits last asked for (`subListKey`). */
  mobileSuits: ListState<MobileSuitAppearanceCardEntity>;
};

export type WorksAction =
  | { type: typeof REQUEST_WORKS; payload: { works: ListRequestPayload } }
  | { type: typeof SET_WORKS; payload: { works: ListSetPayload<WorkCardEntity> } }
  | { type: typeof SET_WORKS_ERROR; payload: { works: ListErrorPayload } }
  | { type: typeof REQUEST_WORK; payload: { works: DetailRequestPayload } }
  | { type: typeof SET_WORK; payload: { works: DetailSetPayload<WorkDetailEntity> } }
  | { type: typeof SET_WORK_ERROR; payload: { works: DetailErrorPayload } }
  | { type: typeof REQUEST_WORK_MOBILE_SUITS; payload: { works: ListRequestPayload } }
  | {
      type: typeof SET_WORK_MOBILE_SUITS;
      payload: { works: ListSetPayload<MobileSuitAppearanceCardEntity> };
    }
  | { type: typeof SET_WORK_MOBILE_SUITS_ERROR; payload: { works: ListErrorPayload } };

export type CombinedWorksStateSlice = CombinedReducer<WorksStateSlice, AppAction>;
