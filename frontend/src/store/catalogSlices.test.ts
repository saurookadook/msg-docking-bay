import { Response as MirageResponse, type Server } from 'miragejs';
import { afterEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockMobileSuitGundam } from '@/__mocks__/workMocks';

import {
  fetchCharacters,
  fetchContinuities,
  fetchMechanicalDesigners,
  fetchMobileSuits,
  fetchOrganizations,
  fetchWork,
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

  it('stores a work under the slug asked for, old or current', async () => {
    server = makeMirageServer({ environment: 'test' });

    const { detailsBySlug } = (
      await run(({ dispatch }) => fetchWork({ dispatch, slug: 'msg' }))
    ).works;

    expect(detailsBySlug.msg).toEqual({
      detail: expect.objectContaining({ slug: mockMobileSuitGundam.slug }),
      errorMessage: null,
      isNotFound: false,
      requestInProgress: false,
    });
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
