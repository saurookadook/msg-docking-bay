import {
  REQUEST_WORK,
  REQUEST_WORKS,
  SET_WORK,
  SET_WORK_ERROR,
  SET_WORKS,
  SET_WORKS_ERROR,
} from '@/store/actionTypes';
import {
  createInitialListState,
  requestDetail,
  requestList,
  setDetail,
  setDetailError,
  setList,
  setListError,
} from '@/store/catalogList';
import { combineReducers } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

import type { CombinedWorksStateSlice, WorksStateSlice } from './reducer.types';

export const initialWorksStateSlice: WorksStateSlice = {
  detailsBySlug: {},
  list: createInitialListState(),
};

const detailsBySlug: CombinedWorksStateSlice['detailsBySlug'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_WORK:
        return requestDetail(stateSlice, action.payload.works);
      case SET_WORK: {
        // NOTE: an old slug's work is stored under its current slug too, so swapping the
        // URL to the current slug does not fetch it again.
        const { detail, slug } = action.payload.works;
        const storedState = setDetail(stateSlice, { detail, slug });
        return detail.slug === slug
          ? storedState
          : setDetail(storedState, { detail, slug: detail.slug });
      }
      case SET_WORK_ERROR:
        return setDetailError(stateSlice, action.payload.works);
      default:
        return stateSlice;
    }
  },
  initialWorksStateSlice.detailsBySlug,
];

const list: CombinedWorksStateSlice['list'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_WORKS:
        return requestList(stateSlice, action.payload.works);
      case SET_WORKS:
        return setList(stateSlice, action.payload.works);
      case SET_WORKS_ERROR:
        return setListError(stateSlice, action.payload.works);
      default:
        return stateSlice;
    }
  },
  initialWorksStateSlice.list,
];

export default combineReducers<WorksStateSlice, AppAction>({
  detailsBySlug,
  list,
});
