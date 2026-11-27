import { Response as MirageResponse, type Request } from 'miragejs';
import { describe, expect, it } from 'vitest';

import {
  DEFAULT_PAGE_SIZE,
  MAX_PAGE_SIZE,
  MAX_SEARCH_LENGTH,
  SEARCH_DEFAULT_LIMIT,
  SEARCH_MAX_LIMIT,
} from '@/constants';

import { findCharacterMock } from './characterMocks';
import {
  buildRoutePath,
  endpointConfigs,
  paginate,
  searchCatalog,
  type AnyEndpointConfig,
  type ApiGetPath,
} from './endpoints';
import { findMechanicalDesignerMobileSuitsMock } from './mechanicalDesignerMocks';
import { findMobileSuitMock, findWorkMobileSuitsMock } from './mobileSuitMocks';
import { findOrganizationMobileSuitsMock } from './organizationMocks';
import { findBySlugOrRedirect } from './peopleMocks';
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

function handle(
  path: ApiGetPath,
  params: Record<string, string>,
  queryParams: Record<string, string> = {},
): unknown {
  const config = endpointConfigs.find((candidate) => candidate.path === path);
  if (config === undefined) throw new Error(`No endpoint config for ${path}`);
  return config.handler({ params, queryParams } as unknown as Request);
}

describe('endpointConfigs', () => {
  it('registers every GET route in the contract', () => {
    expect(endpointConfigs.map(({ path }) => path).toSorted()).toEqual([
      '/api/characters',
      '/api/characters/{character_slug}',
      '/api/continuities',
      '/api/health-check',
      '/api/mechanical-designers',
      '/api/mechanical-designers/{mechanical_designer_slug}',
      '/api/mechanical-designers/{mechanical_designer_slug}/mobile-suits',
      '/api/mobile-suits',
      '/api/mobile-suits/{mobile_suit_slug}',
      '/api/organizations',
      '/api/organizations/{organization_slug}',
      '/api/organizations/{organization_slug}/mobile-suits',
      '/api/search',
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
      '/api/characters/{character_slug}',
      { character_slug: 'char-aznable' },
      'Character not found',
    ],
    [
      '/api/organizations/{organization_slug}',
      { organization_slug: 'aeug' },
      'Organization not found',
    ],
    [
      '/api/mechanical-designers/{mechanical_designer_slug}',
      { mechanical_designer_slug: 'yutaka-izubuchi' },
      'Mechanical designer not found',
    ],
    [
      '/api/organizations/{organization_slug}/mobile-suits',
      { organization_slug: 'aeug' },
      'Organization not found',
    ],
    [
      '/api/mechanical-designers/{mechanical_designer_slug}/mobile-suits',
      { mechanical_designer_slug: 'yutaka-izubuchi' },
      'Mechanical designer not found',
    ],
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

  it('answers old people slugs on their detail and suit routes', () => {
    expect(
      handle('/api/characters/{character_slug}', { character_slug: 'amuro' }),
    ).toEqual({ data: findCharacterMock('amuro-ray') });
    expect(
      handle('/api/organizations/{organization_slug}/mobile-suits', {
        organization_slug: 'earth-federation-universal-century',
      }),
    ).toMatchObject({
      data: [{ mobile_suit: { slug: 'rx-78-2-gundam' } }],
      meta: { total: 1 },
    });
    expect(
      handle('/api/mechanical-designers/{mechanical_designer_slug}/mobile-suits', {
        mechanical_designer_slug: 'katoki-hajime',
      }),
    ).toMatchObject({ data: [{ mobile_suit: { slug: 'rx-78-02-gundam' } }] });
  });

  it("derives a character's piloted suits from the suit fixtures", () => {
    expect(
      findCharacterMock('amuro-ray-origin')?.piloted_mobile_suits.map(
        ({ mobile_suit, work }) => [mobile_suit.slug, work],
      ),
    ).toEqual([['rx-78-02-gundam', null]]);
  });

  it("lists an organization's suits once each, with every link", () => {
    expect(
      findOrganizationMobileSuitsMock('zeonic').map(({ links, mobile_suit }) => [
        mobile_suit.slug,
        links.map(({ role }) => role),
      ]),
    ).toEqual([['ms-06f-zaku-ii', ['manufacturer']]]);
  });

  it("filters an organization's suits by role, as the API does", () => {
    const path = '/api/organizations/{organization_slug}/mobile-suits';
    expect(
      handle(path, { organization_slug: 'earth-federation' }, { role: 'manufacturer' }),
    ).toMatchObject({
      data: [
        { links: [{ role: 'manufacturer' }], mobile_suit: { slug: 'rx-78-2-gundam' } },
      ],
      meta: { total: 1 },
    });
    expect(
      handle(path, { organization_slug: 'earth-federation' }, { role: 'operator' }),
    ).toEqual({ data: [], meta: { limit: DEFAULT_PAGE_SIZE, offset: 0, total: 0 } });
  });

  it("keeps only the asked-for role's links on a suit with several", () => {
    expect(findOrganizationMobileSuitsMock('earth-federation', 'developer')).toEqual(
      [],
    );
    expect(
      findOrganizationMobileSuitsMock('zeonic', 'manufacturer').flatMap(({ links }) =>
        links.map(({ role }) => role),
      ),
    ).toEqual(['manufacturer']);
  });

  it("answers an unknown role with the API's 422", () => {
    const response = handle(
      '/api/organizations/{organization_slug}/mobile-suits',
      { organization_slug: 'earth-federation' },
      { role: 'pilot' },
    );

    expect(response).toBeInstanceOf(MirageResponse);
    const [status, , body] = (response as MirageResponse).toRackResponse();
    expect(status).toBe(422);
    expect(body).toEqual({
      detail: [
        {
          loc: ['query', 'role'],
          msg: "Input should be 'manufacturer', 'operator' or 'developer'",
          type: 'enum',
        },
      ],
    });
  });

  it("lists a designer's suits by name", () => {
    expect(
      findMechanicalDesignerMobileSuitsMock('kunio-okawara').map(
        ({ mobile_suit }) => mobile_suit.slug,
      ),
    ).toEqual(['rx-78-2-gundam', 'rx-78-02-gundam', 'ms-06f-zaku-ii']);
  });

  it.each([
    [
      '/api/organizations/{organization_slug}',
      { organization_slug: 'earth-federation' },
      'earth-federation',
    ],
    [
      '/api/organizations/{organization_slug}',
      { organization_slug: 'earth-federation-universal-century' },
      'earth-federation',
    ],
    [
      '/api/mechanical-designers/{mechanical_designer_slug}',
      { mechanical_designer_slug: 'hajime-katoki' },
      'hajime-katoki',
    ],
    [
      '/api/mechanical-designers/{mechanical_designer_slug}',
      { mechanical_designer_slug: 'katoki-hajime' },
      'hajime-katoki',
    ],
  ] as const)('answers %s for %o with the current slug', (path, params, slug) => {
    expect(handle(path, params)).toMatchObject({ data: { slug } });
  });

  it.each([
    ['/api/characters', ['amuro-ray-origin'], 2],
    ['/api/organizations', ['principality-of-zeon'], 3],
    ['/api/mechanical-designers', ['kunio-okawara'], 3],
  ] as const)('pages %s', (path, slugs, total) => {
    expect(handle(path, {}, { limit: '1', offset: '1' })).toEqual({
      data: slugs.map((slug) => expect.objectContaining({ slug })),
      meta: { limit: 1, offset: 1, total },
    });
  });

  it("pages a person's suit list, and rejects a bad page with a 422", () => {
    expect(
      handle(
        '/api/mechanical-designers/{mechanical_designer_slug}/mobile-suits',
        { mechanical_designer_slug: 'kunio-okawara' },
        { limit: '1', offset: '2' },
      ),
    ).toMatchObject({
      data: [{ mobile_suit: { slug: 'ms-06f-zaku-ii' } }],
      meta: { limit: 1, offset: 2, total: 3 },
    });
    const response = handle(
      '/api/organizations/{organization_slug}/mobile-suits',
      { organization_slug: 'earth-federation' },
      { limit: '0' },
    );
    expect(response).toBeInstanceOf(MirageResponse);
    expect((response as MirageResponse).toRackResponse()[0]).toBe(422);
  });
});

describe('findBySlugOrRedirect', () => {
  it('prefers a current slug to a redirect that names the same slug (D2)', () => {
    const byCurrentSlug = { a: 'row a', b: 'row b' };

    expect(
      findBySlugOrRedirect({ byCurrentSlug, redirects: { a: 'b' }, slug: 'a' }),
    ).toBe('row a');
    expect(
      findBySlugOrRedirect({ byCurrentSlug, redirects: { old: 'b' }, slug: 'old' }),
    ).toBe('row b');
    expect(
      findBySlugOrRedirect({ byCurrentSlug, redirects: {}, slug: 'missing' }),
    ).toBeUndefined();
  });
});

describe('searchCatalog', () => {
  function slugs(queryParams: Record<string, string>): Record<string, string[]> {
    const result = searchCatalog({ queryParams });
    if (result instanceof MirageResponse) throw new Error('Expected a 200 body');
    return Object.fromEntries(
      Object.entries(result.data).map(([kind, cards]) => [
        kind,
        cards.map(({ slug }) => slug),
      ]),
    );
  }

  it('matches each kind as the API does, prefix matches first', () => {
    expect(slugs({ q: 'RX 78-2' })).toEqual({
      characters: [],
      mechanical_designers: [],
      mobile_suits: ['rx-78-2-gundam'],
      organizations: [],
      works: [],
    });
    expect(slugs({ q: 'zeon' }).organizations).toEqual([
      'zeonic',
      'principality-of-zeon',
    ]);
    expect(slugs({ q: 'okawara' }).mechanical_designers).toEqual(['kunio-okawara']);
    expect(slugs({ q: 'red comet' }).works).toEqual([
      'mobile-suit-gundam-the-origin-advent-of-the-red-comet',
    ]);
  });

  it('limits each kind, and totals every match', () => {
    const result = searchCatalog({ queryParams: { q: 'gundam', limit: '1' } });

    expect(result).toMatchObject({
      data: {
        mobile_suits: [{ slug: 'rx-78-2-gundam' }],
        works: [{ slug: 'mobile-suit-gundam' }],
      },
      meta: {
        limit: 1,
        totals: {
          characters: 0,
          mechanical_designers: 0,
          mobile_suits: 3,
          organizations: 0,
          works: 5,
        },
      },
    });
  });

  it.each([{}, { q: '' }, { q: ' -- ' }, { q: '大河原' }])(
    'lists the first rows of each kind for a blank q: %o',
    (queryParams) => {
      expect(searchCatalog({ queryParams })).toMatchObject({
        meta: {
          limit: SEARCH_DEFAULT_LIMIT,
          totals: {
            characters: 2,
            mechanical_designers: 3,
            mobile_suits: 4,
            organizations: 3,
            works: 5,
          },
        },
      });
    },
  );

  it.each([
    [{ limit: '0' }, ['query', 'limit'], 'greater_than_equal'],
    [{ limit: String(SEARCH_MAX_LIMIT + 1) }, ['query', 'limit'], 'less_than_equal'],
    [{ q: 'a'.repeat(MAX_SEARCH_LENGTH + 1) }, ['query', 'q'], 'string_too_long'],
  ])('rejects %o with a 422 like the API', (queryParams, loc, type) => {
    const result = searchCatalog({ queryParams });

    expect(result).toBeInstanceOf(MirageResponse);
    const [code, , body] = (result as MirageResponse).toRackResponse();
    expect(code).toBe(422);
    expect(body).toEqual({ detail: [{ loc, msg: expect.any(String), type }] });
  });

  it('accepts the longest q, counted in characters', () => {
    expect(
      searchCatalog({ queryParams: { q: '大'.repeat(MAX_SEARCH_LENGTH) } }),
    ).not.toBeInstanceOf(MirageResponse);
  });
});

describe('list route filters', () => {
  function listSlugs({
    path,
    queryParams,
  }: {
    path: ApiGetPath;
    queryParams: Record<string, string>;
  }): { slugs: string[]; total: number } {
    const result = handle(path, {}, queryParams);
    if (result instanceof MirageResponse) {
      throw new Error(`[listSlugs] : Expected a 200 body from '${path}'`);
    }
    const { data, meta } = result as {
      data: { slug: string }[];
      meta: { total: number };
    };
    return { slugs: data.map(({ slug }) => slug), total: meta.total };
  }

  it.each([
    [
      '/api/mobile-suits',
      { continuity: 'universal-century' },
      ['rx-78-2-gundam', 'rx-78-02-gundam', 'ms-06f-zaku-ii'],
    ],
    [
      '/api/mobile-suits',
      { work: 'mobile-suit-gundam-the-origin' },
      ['rx-78-02-gundam'],
    ],
    [
      '/api/mobile-suits',
      { unit_type: 'suit', work: 'mobile-suit-gundam' },
      ['rx-78-2-gundam', 'ms-06f-zaku-ii'],
    ],
    ['/api/mobile-suits', { unit_type: 'armor' }, []],
    [
      '/api/works',
      { work_type: 'tv_series' },
      ['mobile-suit-gundam', 'mobile-suit-gundam-the-origin-advent-of-the-red-comet'],
    ],
    [
      '/api/works',
      { continuity: 'universal-century', q: 'origin' },
      [
        'mobile-suit-gundam-the-origin',
        'mobile-suit-gundam-the-origin-advent-of-the-red-comet',
      ],
    ],
    [
      '/api/characters',
      { work: 'mobile-suit-gundam-the-origin' },
      ['amuro-ray-origin'],
    ],
    [
      '/api/organizations',
      { work: 'mobile-suit-gundam' },
      ['earth-federation', 'principality-of-zeon'],
    ],
  ] as const)('filters %s by %o', (path, queryParams, expected) => {
    expect(listSlugs({ path: path, queryParams: queryParams })).toEqual({
      slugs: expected,
      total: expected.length,
    });
  });

  it('applies q to every list route, prefix matches first', () => {
    expect(
      listSlugs({ path: '/api/organizations', queryParams: { q: 'zeon' } }).slugs,
    ).toEqual(['zeonic', 'principality-of-zeon']);
    expect(
      listSlugs({ path: '/api/mechanical-designers', queryParams: { q: 'okawara' } })
        .slugs,
    ).toEqual(['kunio-okawara']);
    expect(
      listSlugs({ path: '/api/mobile-suits', queryParams: { q: 'RX 78-2' } }).slugs,
    ).toEqual(['rx-78-2-gundam']);
  });

  it('filters before paging, so the total counts the matches', () => {
    expect(
      listSlugs({
        path: '/api/mobile-suits',
        queryParams: {
          continuity: 'universal-century',
          limit: '1',
          offset: '1',
        },
      }),
    ).toEqual({ slugs: ['rx-78-02-gundam'], total: 3 });
  });

  it.each([
    ['/api/mobile-suits', { continuity: 'cosmic-era' }],
    ['/api/characters', { work: 'msg' }],
  ] as const)(
    'gives an empty page for an unknown or old slug on %s: %o',
    (path, query) => {
      expect(listSlugs({ path: path, queryParams: query })).toEqual({
        slugs: [],
        total: 0,
      });
    },
  );

  it('rejects every bad param in one 422, like the API', () => {
    const result = handle(
      '/api/mobile-suits',
      {},
      { limit: '0', q: 'a'.repeat(MAX_SEARCH_LENGTH + 1), unit_type: 'tank' },
    );

    expect(result).toBeInstanceOf(MirageResponse);
    const [code, , body] = (result as MirageResponse).toRackResponse();
    expect(code).toBe(422);
    expect(body).toEqual({
      detail: [
        {
          loc: ['query', 'unit_type'],
          msg: "Input should be 'suit', 'armor', 'fighter', 'man_machine', 'worker', 'pod' or 'doll'",
          type: 'enum',
        },
        { loc: ['query', 'q'], msg: expect.any(String), type: 'string_too_long' },
        {
          loc: ['query', 'limit'],
          msg: expect.any(String),
          type: 'greater_than_equal',
        },
      ],
    });
  });

  it('rejects an unknown work type', () => {
    const result = handle('/api/works', {}, { work_type: 'anime' });

    expect((result as MirageResponse).toRackResponse()[0]).toBe(422);
  });
});
