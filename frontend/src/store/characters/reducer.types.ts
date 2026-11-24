import type { CharacterCardEntity } from '@/api';
import type {
  REQUEST_CHARACTERS, // force formatting
  SET_CHARACTERS,
  SET_CHARACTERS_ERROR,
} from '@/store/actionTypes';
import type {
  ListErrorPayload,
  ListRequestPayload,
  ListSetPayload,
  ListState,
} from '@/store/catalogList';
import type { CombinedReducer } from '@/store/combineReducers';
import type { AppAction } from '@/store/types';

export type CharactersStateSlice = {
  list: ListState<CharacterCardEntity>;
};

export type CharactersAction =
  | { type: typeof REQUEST_CHARACTERS; payload: { characters: ListRequestPayload } }
  | {
      type: typeof SET_CHARACTERS;
      payload: { characters: ListSetPayload<CharacterCardEntity> };
    }
  | { type: typeof SET_CHARACTERS_ERROR; payload: { characters: ListErrorPayload } };

export type CombinedCharactersStateSlice = CombinedReducer<
  CharactersStateSlice,
  AppAction
>;
