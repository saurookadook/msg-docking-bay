import type {
  MechanicalDesignerCardEntity,
  MechanicalDesignerDetailEntity,
} from '@/api';
import type {
  REQUEST_MECHANICAL_DESIGNER,
  REQUEST_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNER,
  SET_MECHANICAL_DESIGNER_ERROR,
  SET_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNERS_ERROR,
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

export type MechanicalDesignersStateSlice = {
  detailsBySlug: DetailsBySlug<MechanicalDesignerDetailEntity>;
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
    }
  | {
      type: typeof REQUEST_MECHANICAL_DESIGNER;
      payload: { mechanicalDesigners: DetailRequestPayload };
    }
  | {
      type: typeof SET_MECHANICAL_DESIGNER;
      payload: {
        mechanicalDesigners: DetailSetPayload<MechanicalDesignerDetailEntity>;
      };
    }
  | {
      type: typeof SET_MECHANICAL_DESIGNER_ERROR;
      payload: { mechanicalDesigners: DetailErrorPayload };
    };

export type CombinedMechanicalDesignersStateSlice = CombinedReducer<
  MechanicalDesignersStateSlice,
  AppAction
>;
