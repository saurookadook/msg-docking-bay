import type { MockInstance } from 'vitest';

import type { safeFetch } from '@/utils';

/**
 * @description The request paths a spied `safeFetch.call` was called with for one named
 * fetch, in call order.
 * @example
 * ```ts
 * const fetchSpy = vi.spyOn(safeFetch, 'call');
 * requestPathsFor({ fetchSpy, name: 'fetchWorkMobileSuits' });
 * // ['/api/works/mobile-suit-gundam/mobile-suits']
 * ```
 */
export function requestPathsFor({
  fetchSpy,
  name,
}: {
  fetchSpy: MockInstance<typeof safeFetch.call>;
  name: string;
}): string[] {
  return fetchSpy.mock.calls
    .filter(([{ name: callName }]) => callName === name)
    .map(([, { requestPathname }]) => requestPathname);
}
