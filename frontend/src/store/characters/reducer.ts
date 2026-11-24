import {
  REQUEST_CHARACTERS, // force formatting
  SET_CHARACTERS,
  SET_CHARACTERS_ERROR,
} from '@/store/actionTypes';
import {
  createInitialListState,
  requestList,
  setList,
  setListError,
} from '@/store/catalogList';
import { combineReducers } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

import type {
  CombinedCharactersStateSlice,
  CharactersStateSlice,
} from './reducer.types';

export const initialCharactersStateSlice: CharactersStateSlice = {
  list: createInitialListState(),
};

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
  list,
});
