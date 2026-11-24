import type { CharacterCardEntity, PageMeta } from '@/api';
import {
  REQUEST_CHARACTERS, // force formatting
  SET_CHARACTERS,
  SET_CHARACTERS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogList } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';

export function requestCharacters({
  dispatch,
  search,
}: BaseAction & { search: string }): void {
  return dispatch({ type: REQUEST_CHARACTERS, payload: { characters: { search } } });
}

export function setCharacters({
  dispatch,
  items,
  meta,
  search,
}: BaseAction & {
  items: CharacterCardEntity[];
  meta: PageMeta;
  search: string;
}): void {
  return dispatch({
    type: SET_CHARACTERS,
    payload: { characters: { items, meta, search } },
  });
}

export function setCharactersError({
  dispatch,
  errorMessage,
  search,
}: BaseAction & { errorMessage: string; search: string }): void {
  return dispatch({
    type: SET_CHARACTERS_ERROR,
    payload: { characters: { errorMessage, search } },
  });
}

/**
 * @description Requests one page of `GET /api/characters` for `search` (the API query string,
 * without `?`) and stores it.
 */
export async function fetchCharacters({
  dispatch,
  search,
}: BaseAction & { search: string }): Promise<void> {
  return fetchCatalogList<CharacterCardEntity>({
    listPath: '/api/characters',
    name: fetchCharacters.name,
    onError: (errorMessage) => setCharactersError({ dispatch, errorMessage, search }),
    onRequest: () => requestCharacters({ dispatch, search }),
    onSuccess: ({ data, meta }) =>
      setCharacters({ dispatch, items: data, meta, search }),
    search,
  });
}
