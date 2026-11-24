import type { CharacterCardEntity, CharactersListResponse, PageMeta } from '@/api';
import {
  REQUEST_CHARACTERS, // force formatting
  SET_CHARACTERS,
  SET_CHARACTERS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogList } from '@/store/catalogList';
import type { BaseAction } from '@/store/types';

/** @description Marks the personnel list as loading for `query`. */
export function requestCharacters({
  dispatch,
  query,
}: BaseAction & { query: string }): void {
  return dispatch({ type: REQUEST_CHARACTERS, payload: { characters: { query } } });
}

/** @description Stores one page of personnel for `query`, unless a newer request has replaced it. */
export function setCharacters({
  dispatch,
  items,
  meta,
  query,
}: BaseAction & {
  items: CharacterCardEntity[];
  meta: PageMeta;
  query: string;
}): void {
  return dispatch({
    type: SET_CHARACTERS,
    payload: { characters: { items, meta, query } },
  });
}

/** @description Stores the error for `query`, unless a newer request has replaced it. */
export function setCharactersError({
  dispatch,
  errorMessage,
  query,
}: BaseAction & { errorMessage: string; query: string }): void {
  return dispatch({
    type: SET_CHARACTERS_ERROR,
    payload: { characters: { errorMessage, query } },
  });
}

/**
 * @description Requests one page of `GET /api/characters` for `query` (the API query string,
 * without `?`) and stores it.
 */
export async function fetchCharacters({
  dispatch,
  query,
}: BaseAction & { query: string }): Promise<void> {
  return fetchCatalogList<CharactersListResponse>({
    listPath: '/api/characters',
    name: fetchCharacters.name,
    onError: (errorMessage) => setCharactersError({ dispatch, errorMessage, query }),
    onRequest: () => requestCharacters({ dispatch, query }),
    onSuccess: ({ data, meta }) =>
      setCharacters({ dispatch, items: data, meta, query }),
    query,
  });
}
