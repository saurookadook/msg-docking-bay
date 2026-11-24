import { useEffect, useRef, useState } from 'react';
import { useLocation, useSearchParams } from 'react-router';

import { SEARCH_DEBOUNCE_MS } from '@/constants';
import type { Nullable } from '@/types';
import { withSearchParam } from '@/utils';

function toSearch(searchParams: URLSearchParams): string {
  const search = searchParams.toString();
  return search === '' ? '' : `?${search}`;
}

/**
 * @description The roster search box's draft, written to the URL's `q` once typing
 * pauses for `SEARCH_DEBOUNCE_MS`.
 * @note A typing run pushes one history entry and then replaces it, so Back returns to
 * the list before the search. The run ends on blur, or when the URL changes some other
 * way (Back, a filter, a page link), which also shows that URL's `q` in the box.
 */
export function useDebouncedSearch(): {
  draft: string;
  flushDraft: () => void;
  handleBlur: () => void;
  handleDraftChange: (value: string) => void;
} {
  const [searchParams, setSearchParams] = useSearchParams();
  const { search } = useLocation();
  const urlQ = searchParams.get('q') ?? '';
  const [draft, setDraft] = useState(urlQ);
  const timerRef = useRef<Nullable<ReturnType<typeof setTimeout>>>(null);
  const pendingDraftRef = useRef<Nullable<string>>(null);
  const hasPushedRef = useRef(false);
  const writtenSearchRef = useRef<Nullable<string>>(null);
  const searchParamsRef = useRef(searchParams);

  function clearTimer() {
    if (timerRef.current != null) clearTimeout(timerRef.current);
    timerRef.current = null;
  }

  useEffect(() => {
    searchParamsRef.current = searchParams;
  }, [searchParams]);

  useEffect(() => {
    if (search === writtenSearchRef.current) return;
    // NOTE: the URL changed some other way, so the box follows it and a new run starts.
    clearTimer();
    pendingDraftRef.current = null;
    hasPushedRef.current = false;
    setDraft(urlQ);
  }, [search, urlQ]);

  useEffect(() => clearTimer, []);

  function writeDraft(value: string) {
    pendingDraftRef.current = null;
    const currentSearchParams = searchParamsRef.current;
    const nextSearchParams = withSearchParam({
      name: 'q',
      searchParams: currentSearchParams,
      value,
    });
    if (nextSearchParams.toString() === currentSearchParams.toString()) return;
    writtenSearchRef.current = toSearch(nextSearchParams);
    setSearchParams(nextSearchParams, { replace: hasPushedRef.current });
    hasPushedRef.current = true;
  }

  function handleDraftChange(value: string) {
    setDraft(value);
    clearTimer();
    pendingDraftRef.current = value;
    timerRef.current = setTimeout(() => {
      timerRef.current = null;
      writeDraft(value);
    }, SEARCH_DEBOUNCE_MS);
  }

  /** @description Writes a pending draft now, as Enter does. */
  function flushDraft() {
    const pendingDraft = pendingDraftRef.current;
    clearTimer();
    if (pendingDraft != null) writeDraft(pendingDraft);
  }

  function handleBlur() {
    flushDraft();
    hasPushedRef.current = false;
  }

  return { draft, flushDraft, handleBlur, handleDraftChange };
}
