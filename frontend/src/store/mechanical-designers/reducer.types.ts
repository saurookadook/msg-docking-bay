import type { MechanicalDesignerCardEntity } from '@/api';
import type {
  REQUEST_MECHANICAL_DESIGNERS, // force formatting
  SET_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNERS_ERROR,
} from '@/store/actionTypes';
import type {
  ListErrorPayload,
  ListRequestPayload,
  ListSetPayload,
  ListState,
} from '@/store/catalogList';
import type { CombinedReducer } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

export type MechanicalDesignersStateSlice = {
  list: ListState<MechanicalDesignerCardEntity>;
};

export type MechanicalDesignersAction =
  | {
      type: typeof REQUEST_MECHANICAL_DESIGNERS;
      payload: { mechanicalDesigners: ListRequestPayload };
    }
  | {
      type: typeof SET_MECHANICAL_DESIGNERS;
      payload: { mechanicalDesigners: ListSetPayload<MechanicalDesignerCardEntity> };
    }
  | {
      type: typeof SET_MECHANICAL_DESIGNERS_ERROR;
      payload: { mechanicalDesigners: ListErrorPayload };
    };

export type CombinedMechanicalDesignersStateSlice = CombinedReducer<
  MechanicalDesignersStateSlice,
  AppAction
>;
