import { Response as MirageResponse, type Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockRx782Gundam } from '@/__mocks__/mobileSuitMocks';
import { mockMobileSuitGundam } from '@/__mocks__/workMocks';
import type { HTTPValidationError } from '@/api';

import {
  fetchCharacter,
  fetchCharacters,
  fetchContinuities,
  fetchMechanicalDesigner,
  fetchMechanicalDesignerMobileSuits,
  fetchMechanicalDesigners,
  fetchMobileSuit,
  fetchMobileSuits,
  fetchOrganization,
  fetchOrganizationMobileSuits,
  fetchOrganizations,
  fetchWork,
  fetchWorkMobileSuits,
  fetchWorks,
} from './actions';
import { appReducer, initialAppState, type AppState } from './reducer';
import type { AppAction } from './types';

/** @description Runs an action creator against the real reducer, returning the state. */
async function run(
  action: (args: { dispatch: (action: AppAction) => void }) => Promise<void>,
): Promise<AppState> {
  let state = initialAppState;
  await action({
    dispatch: (dispatched) => {
      state = appReducer(state, dispatched);
    },
  });
  return state;
}

describe('catalog slices', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it.each([
    [
      fetchMobileSuits,
      'mobileSuits',
      'continuity=universal-century&limit=1',
      'rx-78-2-gundam',
      3,
    ],
    [fetchCharacters, 'characters', 'q=origin', 'amuro-ray-origin', 1],
    [
      fetchOrganizations,
      'organizations',
      'work=mobile-suit-gundam',
      'earth-federation',
      2,
    ],
    [fetchWorks, 'works', 'work_type=film', 'mobile-suit-gundam-i', 1],
    [fetchMechanicalDesigners, 'mechanicalDesigners', '', 'hajime-katoki', 3],
  ] as const)(
    '%o stores the page for its query',
    async (fetchList, slice, query, firstSlug, total) => {
      server = makeMirageServer({ environment: 'test' });

      const { list } = (await run(({ dispatch }) => fetchList({ dispatch, query })))[
        slice
      ];

      expect(list).toMatchObject({
        errorMessage: null,
        meta: { total },
        requestInProgress: false,
        query,
      });
      expect(list.items[0]?.slug).toBe(firstSlug);
    },
  );

  it.each([
    [fetchMobileSuits, 'mobileSuits', '/mobile-suits'],
    [fetchCharacters, 'characters', '/characters'],
    [fetchOrganizations, 'organizations', '/organizations'],
    [fetchWorks, 'works', '/works'],
    [fetchMechanicalDesigners, 'mechanicalDesigners', '/mechanical-designers'],
  ] as const)(
    '%o stores a failed request as an error',
    async (fetchList, slice, route) => {
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get(route, () => new MirageResponse(503, {}, {}));
        },
      });

      const { list } = (
        await run(({ dispatch }) => fetchList({ dispatch, query: '' }))
      )[slice];

      expect(list).toMatchObject({
        errorMessage: 'The catalog request failed.',
        items: [],
        requestInProgress: false,
      });
    },
  );

  it("stores a 422 as the API's messages", async () => {
    server = makeMirageServer({ environment: 'test' });

    const { list } = (
      await run(({ dispatch }) =>
        fetchMobileSuits({ dispatch, query: 'unit_type=tank' }),
      )
    ).mobileSuits;

    expect(list.errorMessage).toMatch(/^unit_type: Input should be 'suit'/);
    expect(list.items).toEqual([]);
  });

  it('stores a work under the slug asked for, and an old slug under its current one too', async () => {
    server = makeMirageServer({ environment: 'test' });

    const { detailsBySlug } = (
      await run(({ dispatch }) => fetchWork({ dispatch, slug: 'msg' }))
    ).works;

    const storedWork = {
      detail: expect.objectContaining({ slug: mockMobileSuitGundam.slug }),
      errorMessage: null,
      isNotFound: false,
      requestInProgress: false,
    };
    expect(detailsBySlug.msg).toEqual(storedWork);
    expect(detailsBySlug[mockMobileSuitGundam.slug]).toEqual(storedWork);
  });

  it('marks an unknown work as not found', async () => {
    server = makeMirageServer({ environment: 'test' });

    const { detailsBySlug } = (
      await run(({ dispatch }) => fetchWork({ dispatch, slug: 'turn-a-gundam' }))
    ).works;

    expect(detailsBySlug['turn-a-gundam']).toMatchObject({
      errorMessage: 'Work not found',
      isNotFound: true,
    });
  });

  it('marks a failed work request as an error, not a 404', async () => {
    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get('/works/:work_slug', () => new MirageResponse(503, {}, {}));
      },
    });

    const { detailsBySlug } = (
      await run(({ dispatch }) => fetchWork({ dispatch, slug: 'msg' }))
    ).works;

    expect(detailsBySlug.msg).toMatchObject({
      errorMessage: 'The work request failed.',
      isNotFound: false,
    });
  });

  it('stores a mobile suit under an old slug and under its current one', async () => {
    server = makeMirageServer({ environment: 'test' });

    const { detailsBySlug } = (
      await run(({ dispatch }) => fetchMobileSuit({ dispatch, slug: 'rx-78-2' }))
    ).mobileSuits;

    const storedSuit = {
      detail: expect.objectContaining({
        slug: mockRx782Gundam.slug,
        spec_sheets: expect.any(Array),
      }),
      errorMessage: null,
      isNotFound: false,
      requestInProgress: false,
    };
    expect(detailsBySlug['rx-78-2']).toEqual(storedSuit);
    expect(detailsBySlug[mockRx782Gundam.slug]).toEqual(storedSuit);
  });

  it('stores a mobile suit asked for by its current slug once', async () => {
    server = makeMirageServer({ environment: 'test' });

    const { detailsBySlug } = (
      await run(({ dispatch }) =>
        fetchMobileSuit({ dispatch, slug: mockRx782Gundam.slug }),
      )
    ).mobileSuits;

    expect(Object.keys(detailsBySlug)).toEqual([mockRx782Gundam.slug]);
  });

  it('marks an unknown mobile suit as not found', async () => {
    server = makeMirageServer({ environment: 'test' });

    const { detailsBySlug } = (
      await run(({ dispatch }) => fetchMobileSuit({ dispatch, slug: 'turn-a-gundam' }))
    ).mobileSuits;

    expect(detailsBySlug['turn-a-gundam']).toEqual({
      detail: null,
      errorMessage: 'Mobile suit not found',
      isNotFound: true,
      requestInProgress: false,
    });
  });

  it.each([
    [503, {}, 'The mobile suit request failed.'],
    [
      422,
      {
        detail: [
          {
            loc: ['path', 'mobile_suit_slug'],
            msg: 'Too long',
            type: 'string_too_long',
          },
        ],
      } satisfies HTTPValidationError,
      'mobile_suit_slug: Too long',
    ],
  ])(
    'marks a %i mobile suit answer as an error, not a 404',
    async (status, body, errorMessage) => {
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get(
            '/mobile-suits/:mobile_suit_slug',
            () => new MirageResponse(status, {}, body),
          );
        },
      });

      const { detailsBySlug } = (
        await run(({ dispatch }) =>
          fetchMobileSuit({ dispatch, slug: mockRx782Gundam.slug }),
        )
      ).mobileSuits;

      expect(detailsBySlug[mockRx782Gundam.slug]).toMatchObject({
        detail: null,
        errorMessage,
        isNotFound: false,
      });
    },
  );

  it.each([
    [fetchCharacter, 'characters', 'amuro', 'amuro-ray'],
    [
      fetchOrganization,
      'organizations',
      'earth-federation-universal-century',
      'earth-federation',
    ],
    [fetchMechanicalDesigner, 'mechanicalDesigners', 'katoki-hajime', 'hajime-katoki'],
  ] as const)(
    '%o stores an old slug under itself and under the current one',
    async (fetchDetail, slice, oldSlug, currentSlug) => {
      server = makeMirageServer({ environment: 'test' });

      const { detailsBySlug } = (
        await run(({ dispatch }) => fetchDetail({ dispatch, slug: oldSlug }))
      )[slice];

      const stored = {
        detail: expect.objectContaining({ slug: currentSlug }),
        errorMessage: null,
        isNotFound: false,
        requestInProgress: false,
      };
      expect(detailsBySlug[oldSlug]).toEqual(stored);
      expect(detailsBySlug[currentSlug]).toEqual(stored);
    },
  );

  it.each([
    [fetchCharacter, 'characters', 'Character not found'],
    [fetchOrganization, 'organizations', 'Organization not found'],
    [fetchMechanicalDesigner, 'mechanicalDesigners', 'Mechanical designer not found'],
  ] as const)(
    '%o marks an unknown slug as not found',
    async (fetchDetail, slice, message) => {
      server = makeMirageServer({ environment: 'test' });

      const { detailsBySlug } = (
        await run(({ dispatch }) => fetchDetail({ dispatch, slug: 'char-aznable' }))
      )[slice];

      expect(detailsBySlug['char-aznable']).toEqual({
        detail: null,
        errorMessage: message,
        isNotFound: true,
        requestInProgress: false,
      });
    },
  );

  it.each([
    [
      fetchCharacter,
      'characters',
      '/characters/:character_slug',
      'The character request failed.',
    ],
    [
      fetchOrganization,
      'organizations',
      '/organizations/:organization_slug',
      'The organization request failed.',
    ],
    [
      fetchMechanicalDesigner,
      'mechanicalDesigners',
      '/mechanical-designers/:mechanical_designer_slug',
      'The mechanical designer request failed.',
    ],
  ] as const)(
    '%o marks a failed request as an error, not a 404',
    async (fetchDetail, slice, route, errorMessage) => {
      server = makeMirageServer({
        environment: 'test',
        overrides: (mirage) => {
          mirage.get(route, () => new MirageResponse(503, {}, {}));
        },
      });

      const { detailsBySlug } = (
        await run(({ dispatch }) => fetchDetail({ dispatch, slug: 'amuro-ray' }))
      )[slice];

      expect(detailsBySlug['amuro-ray']).toMatchObject({
        detail: null,
        errorMessage,
        isNotFound: false,
      });
    },
  );

  it("stores a page of a work's suits under its slug and query", async () => {
    server = makeMirageServer({ environment: 'test' });

    const { mobileSuits } = (
      await run(({ dispatch }) =>
        fetchWorkMobileSuits({
          dispatch,
          query: 'limit=1',
          slug: 'mobile-suit-gundam',
        }),
      )
    ).works;

    expect(mobileSuits).toMatchObject({
      errorMessage: null,
      items: [{ is_debut: true, slug: 'rx-78-2-gundam' }],
      meta: { limit: 1, offset: 0, total: 2 },
      query: 'mobile-suit-gundam?limit=1',
      requestInProgress: false,
    });
  });

  it("stores a page of a designer's suits under their slug and query", async () => {
    server = makeMirageServer({ environment: 'test' });

    const { mobileSuits } = (
      await run(({ dispatch }) =>
        fetchMechanicalDesignerMobileSuits({
          dispatch,
          query: 'limit=1&offset=2',
          slug: 'kunio-okawara',
        }),
      )
    ).mechanicalDesigners;

    expect(mobileSuits).toMatchObject({
      errorMessage: null,
      items: [{ mobile_suit: { slug: 'ms-06f-zaku-ii' } }],
      meta: { limit: 1, offset: 2, total: 3 },
      query: 'kunio-okawara?limit=1&offset=2',
      requestInProgress: false,
    });
  });

  it.each([
    [fetchWorkMobileSuits, 'works', 'Work not found'],
    [
      fetchMechanicalDesignerMobileSuits,
      'mechanicalDesigners',
      'Mechanical designer not found',
    ],
  ] as const)(
    '%o stores a failed sub-list request as an error',
    async (fetchSubList, slice, message) => {
      server = makeMirageServer({ environment: 'test' });

      const { mobileSuits } = (
        await run(({ dispatch }) =>
          fetchSubList({ dispatch, query: '', slug: 'turn-a-gundam' }),
        )
      )[slice];

      expect(mobileSuits).toMatchObject({
        errorMessage: message,
        items: [],
        query: 'turn-a-gundam?',
      });
    },
  );

  it("stores each role's suits in its own section", async () => {
    server = makeMirageServer({ environment: 'test' });

    const { mobileSuitsByRole } = (
      await run(async ({ dispatch }) => {
        await fetchOrganizationMobileSuits({
          dispatch,
          query: 'role=manufacturer',
          role: 'manufacturer',
          slug: 'earth-federation',
        });
        await fetchOrganizationMobileSuits({
          dispatch,
          query: 'role=operator',
          role: 'operator',
          slug: 'earth-federation',
        });
      })
    ).organizations;

    expect(mobileSuitsByRole.manufacturer).toMatchObject({
      items: [{ mobile_suit: { slug: 'rx-78-2-gundam' } }],
      meta: { total: 1 },
      query: 'earth-federation?role=manufacturer',
    });
    expect(mobileSuitsByRole.operator).toMatchObject({
      items: [],
      meta: { total: 0 },
      query: 'earth-federation?role=operator',
    });
    expect(mobileSuitsByRole.developer).toEqual(
      initialAppState.organizations.mobileSuitsByRole.developer,
    );
  });

  it('loads every continuity, or the error', async () => {
    server = makeMirageServer({ environment: 'test' });
    expect((await run(fetchContinuities)).continuities).toEqual({
      continuities: [expect.objectContaining({ slug: 'universal-century' })],
      continuitiesErrorMessage: null,
      continuitiesLoaded: true,
      continuitiesRequestInProgress: false,
    });
    server.shutdown();

    server = makeMirageServer({
      environment: 'test',
      overrides: (mirage) => {
        mirage.get(
          '/continuities',
          () => new MirageResponse(503, {}, { detail: 'Down' }),
        );
      },
    });
    expect((await run(fetchContinuities)).continuities).toMatchObject({
      continuities: [],
      continuitiesErrorMessage: 'Down',
      continuitiesLoaded: false,
    });
  });
});
