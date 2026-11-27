import {
  REQUEST_CHARACTER,
  REQUEST_CHARACTERS,
  SET_CHARACTER,
  SET_CHARACTER_ERROR,
  SET_CHARACTERS,
  SET_CHARACTERS_ERROR,
} from '@/store/actionTypes';
import {
  createInitialListState,
  requestDetail,
  requestList,
  setDetailError,
  setDetailUnderSlugs,
  setList,
  setListError,
} from '@/store/catalogList';
import { combineReducers } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

import type {
  CharactersStateSlice,
  CombinedCharactersStateSlice,
} from './reducer.types';

export const initialCharactersStateSlice: CharactersStateSlice = {
  detailsBySlug: {},
  list: createInitialListState(),
};

const detailsBySlug: CombinedCharactersStateSlice['detailsBySlug'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_CHARACTER:
        return requestDetail(stateSlice, action.payload.characters);
      case SET_CHARACTER:
        return setDetailUnderSlugs(stateSlice, action.payload.characters);
      case SET_CHARACTER_ERROR:
        return setDetailError(stateSlice, action.payload.characters);
      default:
        return stateSlice;
    }
  },
  initialCharactersStateSlice.detailsBySlug,
];

const list: CombinedCharactersStateSlice['list'] = [
  (stateSlice, action) => {
    switch (action.type) {
      case REQUEST_CHARACTERS:
        return requestList(stateSlice, action.payload.characters);
      case SET_CHARACTERS:
        return setList(stateSlice, action.payload.characters);
      case SET_CHARACTERS_ERROR:
        return setListError(stateSlice, action.payload.characters);
      default:
        return stateSlice;
    }
  },
  initialCharactersStateSlice.list,
];

export default combineReducers<CharactersStateSlice, AppAction>({
  detailsBySlug,
  list,
});
