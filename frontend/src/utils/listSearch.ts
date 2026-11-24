/**
 * @description The API query string, without `?`, for a list page: only `keys` with a
 * non-blank value, sorted by key, so the same state always gives the same string.
 * @example
 * ```ts
 * listSearch({ keys: ['q', 'unit_type'], searchParams: new URLSearchParams('unit_type=suit&foo=1&q=') });
 * // 'unit_type=suit'
 * ```
 */
export function listSearch({
  keys,
  searchParams,
}: {
  keys: readonly string[];
  searchParams: URLSearchParams;
}): string {
  const picked = new URLSearchParams();
  for (const key of keys.toSorted()) {
    const value = searchParams.get(key)?.trim();
    if (value != null && value !== '') picked.set(key, value);
  }
  return picked.toString();
}

/**
 * @description The search params with `name` set to `value`, or removed when `value` is
 * blank or `null`. It also drops `offset`: a new query starts on its first page.
 */
export function withSearchParam({
  name,
  searchParams,
  value,
}: {
  name: string;
  searchParams: URLSearchParams;
  value: string | null;
}): URLSearchParams {
  const nextSearchParams = new URLSearchParams(searchParams);
  nextSearchParams.delete('offset');
  const trimmed = value?.trim() ?? '';
  if (trimmed === '') {
    nextSearchParams.delete(name);
  } else {
    nextSearchParams.set(name, trimmed);
  }
  return nextSearchParams;
}

/** @description The search params without any of `names`, and without `offset`. */
export function withoutSearchParams({
  names,
  searchParams,
}: {
  names: readonly string[];
  searchParams: URLSearchParams;
}): URLSearchParams {
  const nextSearchParams = new URLSearchParams(searchParams);
  for (const name of [...names, 'offset']) nextSearchParams.delete(name);
  return nextSearchParams;
}
