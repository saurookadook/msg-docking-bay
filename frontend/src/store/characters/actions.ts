import type {
  CharacterCardEntity,
  CharacterDetailEntity,
  CharacterResponse,
  CharactersListResponse,
  PageMeta,
} from '@/api';
import {
  REQUEST_CHARACTER,
  REQUEST_CHARACTERS,
  SET_CHARACTER,
  SET_CHARACTER_ERROR,
  SET_CHARACTERS,
  SET_CHARACTERS_ERROR,
} from '@/store/actionTypes';
import { fetchCatalogDetail, fetchCatalogList } from '@/store/catalogList';
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

/**
 * @description Marks the character under `slug` as loading.
 * @note `slug` is the URL slug asked for (`amuro-ray`): an old one too.
 */
export function requestCharacter({
  dispatch,
  slug,
}: BaseAction & { slug: string }): void {
  return dispatch({ type: REQUEST_CHARACTER, payload: { characters: { slug } } });
}

/**
 * @description Stores the character fetched for `slug`.
 * @note `slug` is the URL slug asked for (`amuro-ray`): an old one too.
 */
export function setCharacter({
  detail,
  dispatch,
  slug,
}: BaseAction & { detail: CharacterDetailEntity; slug: string }): void {
  return dispatch({ type: SET_CHARACTER, payload: { characters: { detail, slug } } });
}

/**
 * @description Stores the error for the character under `slug`; `isNotFound` marks a 404.
 * @note `slug` is the URL slug asked for (`amuro-ray`): an old one too.
 */
export function setCharacterError({
  dispatch,
  errorMessage,
  isNotFound,
  slug,
}: BaseAction & { errorMessage: string; isNotFound: boolean; slug: string }): void {
  return dispatch({
    type: SET_CHARACTER_ERROR,
    payload: { characters: { errorMessage, isNotFound, slug } },
  });
}

/**
 * @description Requests `GET /api/characters/{character_slug}` and stores the character under
 * `slug`, the slug asked for. An old slug stores the renamed character, whose `slug` is
 * current, under both.
 */
export async function fetchCharacter({
  dispatch,
  slug,
}: BaseAction & { slug: string }): Promise<void> {
  return fetchCatalogDetail<CharacterResponse>({
    detailPath: `/api/characters/${encodeURIComponent(slug)}`,
    fallbackErrorMessage: 'The character request failed.',
    name: fetchCharacter.name,
    onError: ({ errorMessage, isNotFound }) =>
      setCharacterError({ dispatch, errorMessage, isNotFound, slug }),
    onRequest: () => requestCharacter({ dispatch, slug }),
    onSuccess: (detail) => setCharacter({ detail, dispatch, slug }),
  });
}
