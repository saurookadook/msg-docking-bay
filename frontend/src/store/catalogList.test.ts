import { describe, expect, it } from 'vitest';

import { mockRx782Gundam, mockZakuII } from '@/__mocks__/mobileSuitMocks';
import { mockMobileSuitGundam } from '@/__mocks__/workMocks';
import type { MobileSuitCardEntity } from '@/api';
import { SafeFetchError } from '@/utils';

import {
  catalogErrorMessage,
  createInitialListState,
  requestDetail,
  requestList,
  setDetail,
  setDetailError,
  setList,
  setListError,
} from './catalogList';

const meta = { limit: 50, offset: 0, total: 1 };

describe('list transitions', () => {
  it('keeps the shown rows while a new query loads', () => {
    const shown = setList(
      requestList(createInitialListState<MobileSuitCardEntity>(), { search: '' }),
      {
        items: [mockRx782Gundam],
        meta,
        search: '',
      },
    );

    expect(requestList(shown, { search: 'q=zaku' })).toEqual({
      errorMessage: null,
      items: [mockRx782Gundam],
      meta,
      requestInProgress: true,
      search: 'q=zaku',
    });
  });

  it('drops a page that answers an older query', () => {
    const loading = requestList(createInitialListState<MobileSuitCardEntity>(), {
      search: 'q=zaku',
    });

    expect(setList(loading, { items: [mockRx782Gundam], meta, search: 'q=gu' })).toBe(
      loading,
    );
    expect(setListError(loading, { errorMessage: 'late', search: 'q=gu' })).toBe(
      loading,
    );
    expect(setList(loading, { items: [mockZakuII], meta, search: 'q=zaku' })).toEqual({
      errorMessage: null,
      items: [mockZakuII],
      meta,
      requestInProgress: false,
      search: 'q=zaku',
    });
  });

  it('clears the rows when the current query fails', () => {
    const loading = requestList(
      setList(
        requestList(createInitialListState<MobileSuitCardEntity>(), { search: '' }),
        {
          items: [mockRx782Gundam],
          meta,
          search: '',
        },
      ),
      { search: 'unit_type=tank' },
    );

    expect(
      setListError(loading, { errorMessage: 'bad', search: 'unit_type=tank' }),
    ).toEqual({
      errorMessage: 'bad',
      items: [],
      meta: null,
      requestInProgress: false,
      search: 'unit_type=tank',
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
