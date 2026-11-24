import type { Server } from 'miragejs';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { mockRx782Gundam, mockZakuII } from '@/__mocks__/mobileSuitMocks';
import { mockMobileSuitGundam } from '@/__mocks__/workMocks';
import type { MobileSuitCardEntity, MobileSuitsListResponse } from '@/api';
import { SafeFetchError } from '@/utils';

import {
  catalogErrorMessage,
  createInitialListState,
  fetchCatalogList,
  requestDetail,
  requestList,
  setDetail,
  setDetailError,
  setList,
  setListError,
} from './catalogList';

const mockPageMeta = { limit: 50, offset: 0, total: 1 };

describe('list transitions', () => {
  it('keeps the shown rows while a new query loads', () => {
    const shown = setList(
      requestList(createInitialListState<MobileSuitCardEntity>(), { query: '' }),
      {
        items: [mockRx782Gundam],
        meta: mockPageMeta,
        query: '',
      },
    );

    expect(requestList(shown, { query: 'q=zaku' })).toEqual({
      errorMessage: null,
      items: [mockRx782Gundam],
      meta: mockPageMeta,
      requestInProgress: true,
      query: 'q=zaku',
    });
  });

  it('drops a page that answers an older query', () => {
    const loading = requestList(createInitialListState<MobileSuitCardEntity>(), {
      query: 'q=zaku',
    });

    expect(
      setList(loading, {
        items: [mockRx782Gundam],
        meta: mockPageMeta,
        query: 'q=gu',
      }),
    ).toBe(loading);
    expect(setListError(loading, { errorMessage: 'late', query: 'q=gu' })).toBe(
      loading,
    );
    expect(
      setList(loading, { items: [mockZakuII], meta: mockPageMeta, query: 'q=zaku' }),
    ).toEqual({
      errorMessage: null,
      items: [mockZakuII],
      meta: mockPageMeta,
      requestInProgress: false,
      query: 'q=zaku',
    });
  });

  it('clears the rows when the current query fails', () => {
    const loading = requestList(
      setList(
        requestList(createInitialListState<MobileSuitCardEntity>(), { query: '' }),
        {
          items: [mockRx782Gundam],
          meta: mockPageMeta,
          query: '',
        },
      ),
      { query: 'unit_type=tank' },
    );

    expect(
      setListError(loading, { errorMessage: 'bad', query: 'unit_type=tank' }),
    ).toEqual({
      errorMessage: 'bad',
      items: [],
      meta: null,
      requestInProgress: false,
      query: 'unit_type=tank',
    });
  });
});

describe('detail transitions', () => {
  it('tracks each slug on its own, keeping a detail while it reloads', () => {
    const loaded = setDetail(requestDetail({}, { slug: 'msg' }), {
      detail: mockMobileSuitGundam,
      slug: 'msg',
    });

    expect(requestDetail(loaded, { slug: 'msg' }).msg).toEqual({
      detail: mockMobileSuitGundam,
      errorMessage: null,
      isNotFound: false,
      requestInProgress: true,
    });
    expect(
      setDetailError(loaded, {
        errorMessage: 'Work not found',
        isNotFound: true,
        slug: 'x',
      }),
    ).toEqual({
      msg: loaded.msg,
      x: {
        detail: null,
        errorMessage: 'Work not found',
        isNotFound: true,
        requestInProgress: false,
      },
    });
  });
});

describe('catalogErrorMessage', () => {
  function fetchError(detail: unknown): SafeFetchError {
    return new SafeFetchError({
      callerName: 'test',
      detail,
      requestURL: '/api',
      status: 422,
    });
  }

  it.each([
    [fetchError('Work not found'), 'Work not found'],
    [
      fetchError([
        {
          loc: ['query', 'unit_type'],
          msg: 'Input should be a unit type',
          type: 'enum',
        },
        { loc: ['query', 'limit'], msg: 'Too small', type: 'greater_than_equal' },
      ]),
      'unit_type: Input should be a unit type; limit: Too small',
    ],
    [fetchError([{ loc: [], msg: 'Bad', type: 'x' }]), 'request: Bad'],
    [fetchError([]), 'fallback'],
    [fetchError(null), 'fallback'],
    [new Error('offline'), 'fallback'],
  ])('shows %o as %s', (error, message) => {
    expect(catalogErrorMessage({ error, fallback: 'fallback' })).toBe(message);
  });
});

describe('fetchCatalogList', () => {
  let server: Server;

  afterEach(() => {
    server.shutdown();
  });

  it('lets a failure in storing the page surface, instead of calling it a failed request', async () => {
    server = makeMirageServer({ environment: 'test' });
    const onError = vi.fn();

    await expect(
      fetchCatalogList<MobileSuitsListResponse>({
        listPath: '/api/mobile-suits',
        name: 'test',
        onError,
        onRequest: vi.fn(),
        onSuccess: () => {
          throw new Error('[test] : the store rejected the page');
        },
        query: '',
      }),
    ).rejects.toThrow('the store rejected the page');
    expect(onError).not.toHaveBeenCalled();
  });
});
