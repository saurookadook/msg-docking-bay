import type { CharacterCardEntity, CharacterDetailEntity } from '@/api';
import type {
  REQUEST_CHARACTER,
  REQUEST_CHARACTERS,
  SET_CHARACTER,
  SET_CHARACTER_ERROR,
  SET_CHARACTERS,
  SET_CHARACTERS_ERROR,
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

export type CharactersStateSlice = {
  detailsBySlug: DetailsBySlug<CharacterDetailEntity>;
  list: ListState<CharacterCardEntity>;
};

export type CharactersAction =
  | { type: typeof REQUEST_CHARACTERS; payload: { characters: ListRequestPayload } }
  | {
      type: typeof SET_CHARACTERS;
      payload: { characters: ListSetPayload<CharacterCardEntity> };
    }
  | { type: typeof SET_CHARACTERS_ERROR; payload: { characters: ListErrorPayload } }
  | { type: typeof REQUEST_CHARACTER; payload: { characters: DetailRequestPayload } }
  | {
      type: typeof SET_CHARACTER;
      payload: { characters: DetailSetPayload<CharacterDetailEntity> };
    }
  | { type: typeof SET_CHARACTER_ERROR; payload: { characters: DetailErrorPayload } };

export type CombinedCharactersStateSlice = CombinedReducer<
  CharactersStateSlice,
  AppAction
>;
