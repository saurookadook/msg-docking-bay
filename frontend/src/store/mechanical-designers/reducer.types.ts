import type {
  DesignedMobileSuitEntity,
  MechanicalDesignerCardEntity,
  MechanicalDesignerDetailEntity,
} from '@/api';
import type {
  REQUEST_MECHANICAL_DESIGNER,
  REQUEST_MECHANICAL_DESIGNER_MOBILE_SUITS,
  REQUEST_MECHANICAL_DESIGNERS,
  SET_MECHANICAL_DESIGNER,
  SET_MECHANICAL_DESIGNER_ERROR,
  SET_MECHANICAL_DESIGNER_MOBILE_SUITS,
  SET_MECHANICAL_DESIGNER_MOBILE_SUITS_ERROR,
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
  /** @description The page of the designer's suits last asked for (`subListKey`). */
  mobileSuits: ListState<DesignedMobileSuitEntity>;
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
    }
  | {
      type: typeof REQUEST_MECHANICAL_DESIGNER_MOBILE_SUITS;
      payload: { mechanicalDesigners: ListRequestPayload };
    }
  | {
      type: typeof SET_MECHANICAL_DESIGNER_MOBILE_SUITS;
      payload: { mechanicalDesigners: ListSetPayload<DesignedMobileSuitEntity> };
    }
  | {
      type: typeof SET_MECHANICAL_DESIGNER_MOBILE_SUITS_ERROR;
      payload: { mechanicalDesigners: ListErrorPayload };
    };

export type CombinedMechanicalDesignersStateSlice = CombinedReducer<
  MechanicalDesignersStateSlice,
  AppAction
>;
