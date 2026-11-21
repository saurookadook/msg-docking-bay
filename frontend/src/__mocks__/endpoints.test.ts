import { Response as MirageResponse, type Request } from 'miragejs';
import { describe, expect, it } from 'vitest';

import { DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE } from '@/constants';

import {
  buildRoutePath,
  endpointConfigs,
  paginate,
  type AnyEndpointConfig,
  type ApiGetPath,
} from './endpoints';
import { findMobileSuitMock, findWorkMobileSuitsMock } from './mobileSuitMocks';
import { findWorkMock } from './workMocks';

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

describe('paginate validation', () => {
  const items = ['a', 'b', 'c'];

  it.each([
    [{ limit: '0' }, ['query', 'limit'], 'greater_than_equal'],
    [{ limit: '101' }, ['query', 'limit'], 'less_than_equal'],
    [{ limit: '2.5' }, ['query', 'limit'], 'int_parsing'],
    [{ offset: '-1' }, ['query', 'offset'], 'greater_than_equal'],
    [{ offset: 'abc' }, ['query', 'offset'], 'int_parsing'],
  ])('rejects %o with a 422 like the API', (queryParams, loc, type) => {
    const result = paginate(items, { queryParams });

    expect(result).toBeInstanceOf(MirageResponse);
    const [code, , body] = (result as MirageResponse).toRackResponse();
    expect(code).toBe(422);
    expect(body).toEqual({ detail: [{ loc, msg: expect.any(String), type }] });
  });

  it('uses the API defaults when the query gives none', () => {
    expect(paginate(items, { queryParams: {} })).toEqual({
      data: items,
      meta: { limit: DEFAULT_PAGE_SIZE, offset: 0, total: 3 },
    });
  });

  it('accepts the largest page the API allows', () => {
    expect(
      paginate(items, { queryParams: { limit: String(MAX_PAGE_SIZE) } }),
    ).toMatchObject({
      meta: { limit: MAX_PAGE_SIZE },
    });
  });
});

function handle(path: ApiGetPath, params: Record<string, string>): unknown {
  const config = endpointConfigs.find((candidate) => candidate.path === path);
  if (config === undefined) throw new Error(`No endpoint config for ${path}`);
  return config.handler({ params, queryParams: {} } as unknown as Request);
}

describe('endpointConfigs', () => {
  it('registers every GET route in the contract', () => {
    expect(endpointConfigs.map(({ path }) => path).toSorted()).toEqual([
      '/api/continuities',
      '/api/health-check',
      '/api/mobile-suits',
      '/api/mobile-suits/{mobile_suit_slug}',
      '/api/works',
      '/api/works/{work_slug}',
      '/api/works/{work_slug}/mobile-suits',
    ]);
  });

  it('answers an old suit slug with the renamed suit', () => {
    expect(
      handle('/api/mobile-suits/{mobile_suit_slug}', { mobile_suit_slug: 'rx-78-2' }),
    ).toEqual({
      data: findMobileSuitMock('rx-78-2-gundam'),
    });
    expect(findMobileSuitMock('rx-78-2')?.slug).toBe('rx-78-2-gundam');
  });

  it('answers an old work slug on both work routes with the renamed work', () => {
    expect(handle('/api/works/{work_slug}', { work_slug: 'msg' })).toEqual({
      data: findWorkMock('mobile-suit-gundam'),
    });
    expect(
      handle('/api/works/{work_slug}/mobile-suits', { work_slug: 'msg' }),
    ).toMatchObject({
      data: [{ slug: 'rx-78-2-gundam' }, { slug: 'ms-06f-zaku-ii' }],
      meta: { total: 2 },
    });
  });

  it.each([
    [
      '/api/mobile-suits/{mobile_suit_slug}',
      { mobile_suit_slug: 'gp01' },
      'Mobile suit not found',
    ],
    ['/api/works/{work_slug}', { work_slug: 'turn-a-gundam' }, 'Work not found'],
    [
      '/api/works/{work_slug}/mobile-suits',
      { work_slug: 'turn-a-gundam' },
      'Work not found',
    ],
  ] as const)('answers an unknown slug on %s with a 404', (path, params, detail) => {
    const response = handle(path, params);

    expect(response).toBeInstanceOf(MirageResponse);
    const [code, , body] = (response as MirageResponse).toRackResponse();
    expect(code).toBe(404);
    expect(body).toEqual({ detail });
  });

  it("lists a work's suits debuts first", () => {
    expect(
      findWorkMobileSuitsMock('mobile-suit-gundam-i').map(({ slug, is_debut }) => [
        slug,
        is_debut,
      ]),
    ).toEqual([
      ['rx-78-2-gundam', false],
      ['ms-06f-zaku-ii', false],
    ]);
    expect(
      findWorkMobileSuitsMock('it-moves-gundam-follow-your-dreams').map(
        ({ slug }) => slug,
      ),
    ).toEqual(['rx-78f00-gundam']);
  });
});
