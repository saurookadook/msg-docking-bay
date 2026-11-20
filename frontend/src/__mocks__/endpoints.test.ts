import { describe, expect, it } from 'vitest';

import { buildRoutePath, paginate, type AnyEndpointConfig } from './endpoints';

describe('buildRoutePath', () => {
  it.each([
    ['/api/health-check', '/health-check'],
    ['/api/mobile-suits/{mobile_suit_slug}', '/mobile-suits/:mobile_suit_slug'],
  ])('turns %s into %s', (path, routePath) => {
    expect(buildRoutePath(path)).toBe(routePath);
  });
});

describe('paginate', () => {
  const items = ['a', 'b', 'c'];

  it('returns the requested page with its meta', () => {
    expect(paginate(items, { queryParams: { limit: '2', offset: '0' } })).toEqual({
      data: ['a', 'b'],
      meta: { limit: 2, offset: 0, total: 3 },
    });
  });

  it('returns an empty page, with the real total, for an offset past the end', () => {
    expect(paginate(items, { queryParams: { limit: '2', offset: '5' } })).toEqual({
      data: [],
      meta: { limit: 2, offset: 5, total: 3 },
    });
  });
});

describe('AnyEndpointConfig', () => {
  it('rejects a config for an unknown path or with the wrong body', () => {
    // Never registered: `tsc -b` checks these through tsconfig.test.json.
    const configs: AnyEndpointConfig[] = [
      // @ts-expect-error: '/api/not-a-route' isn't a path in the generated contract
      { path: '/api/not-a-route', handler: () => ({}) },
      {
        path: '/api/health-check',
        // @ts-expect-error: the health check's status is the literal 'ok'
        handler: () => ({ data: { status: 'down' } }),
      },
    ];

    expect(configs).toHaveLength(2);
  });
});
