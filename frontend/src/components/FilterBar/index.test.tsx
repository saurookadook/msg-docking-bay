import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createMemoryRouter, RouterProvider } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { SEARCH_DEBOUNCE_MS } from '@/constants';

import { FilterBar, type FilterBarProps } from '.';

const props: FilterBarProps = {
  chips: [{ label: 'Work', param: 'work', valueLabel: 'Mobile Suit Gundam' }],
  searchLabel: 'Search mobile suits',
  selects: [
    {
      label: 'Unit type',
      options: [
        { label: 'Mobile Suit', value: 'suit' },
        { label: 'Mobile Armor', value: 'armor' },
      ],
      param: 'unit_type',
    },
  ],
};

/**
 * @note TEST-17: this builds its own memory router, not the app's `routerConfig`, so the
 * test can read and step through the history the filter bar writes.
 */
function renderFilterBar(initialEntry = '/mobile-suits') {
  const router = createMemoryRouter(
    [{ element: <FilterBar {...props} />, path: '/mobile-suits' }],
    { initialEntries: ['/', initialEntry], initialIndex: 1 },
  );
  render(<RouterProvider router={router} />);
  const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
  return { router, user };
}

const searchBox = () => screen.getByRole('searchbox', { name: 'Search mobile suits' });

describe('FilterBar', () => {
  beforeEach(() => {
    vi.useFakeTimers({
      shouldAdvanceTime: true,
      toFake: ['setTimeout', 'clearTimeout', 'Date'],
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('writes q once typing pauses, dropping the offset', async () => {
    const { router, user } = renderFilterBar('/mobile-suits?offset=50');

    await user.type(searchBox(), 'zaku');
    expect(router.state.location.search).toBe('?offset=50');

    act(() => {
      vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS);
    });
    expect(router.state.location.search).toBe('?q=zaku');
  });

  it('pushes one history entry per typing run, so Back leaves the search', async () => {
    const { router, user } = renderFilterBar();

    await user.type(searchBox(), 'gu');
    act(() => {
      vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS);
    });
    await user.type(searchBox(), 'ndam');
    act(() => {
      vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS);
    });
    expect(router.state.location.search).toBe('?q=gundam');

    await act(() => router.navigate(-1));
    expect(router.state.location.pathname).toBe('/mobile-suits');
    expect(router.state.location.search).toBe('');
    expect(searchBox()).toHaveValue('');
  });

  it('starts a new run after the box loses focus', async () => {
    const { router, user } = renderFilterBar();

    await user.type(searchBox(), 'gu');
    act(() => {
      vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS);
    });
    await user.tab();
    await user.type(searchBox(), 'ndam');
    act(() => {
      vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS);
    });

    await act(() => router.navigate(-1));
    expect(router.state.location.search).toBe('?q=gu');
    expect(searchBox()).toHaveValue('gu');
  });

  it('searches at once on Enter, and on blur', async () => {
    const { router, user } = renderFilterBar();

    await user.type(searchBox(), 'zaku{Enter}');
    expect(router.state.location.search).toBe('?q=zaku');

    await user.type(searchBox(), ' ii');
    await user.tab();
    expect(router.state.location.search).toBe('?q=zaku+ii');
  });

  it('removes q for a blank search, and skips a write that changes nothing', async () => {
    const { router, user } = renderFilterBar('/mobile-suits?q=zaku');
    expect(searchBox()).toHaveValue('zaku');

    await user.clear(searchBox());
    await user.type(searchBox(), '  ');
    act(() => {
      vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS);
    });
    expect(router.state.location.search).toBe('');

    await user.type(searchBox(), '{Enter}');
    expect(router.state.location.search).toBe('');
  });

  it('adds no history entry when the trimmed q is unchanged', async () => {
    const { router, user } = renderFilterBar('/mobile-suits?q=zaku');

    await user.type(searchBox(), ' ');
    act(() => {
      vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS);
    });
    expect(router.state.location.search).toBe('?q=zaku');

    await act(() => router.navigate(-1));
    expect(router.state.location.pathname).toBe('/');
  });

  it('applies a select on change, and shows the URL value', async () => {
    const { router, user } = renderFilterBar('/mobile-suits?offset=50');
    const select = screen.getByRole('combobox', { name: 'Unit type' });

    await user.selectOptions(select, 'Mobile Armor');
    expect(router.state.location.search).toBe('?unit_type=armor');
    expect(select).toHaveValue('armor');

    await user.selectOptions(select, 'All');
    expect(router.state.location.search).toBe('');
  });

  it('shows a chip only while its param is set, and removes it', async () => {
    const { router, user } = renderFilterBar(
      '/mobile-suits?work=mobile-suit-gundam&q=zaku',
    );

    expect(screen.getByRole('list', { name: 'Active filters' })).toHaveTextContent(
      'Work: Mobile Suit Gundam',
    );
    await user.click(
      screen.getByRole('button', {
        name: 'Remove the work filter: Mobile Suit Gundam',
      }),
    );
    expect(router.state.location.search).toBe('?q=zaku');
    expect(
      screen.queryByRole('list', { name: 'Active filters' }),
    ).not.toBeInTheDocument();
  });

  it('clears every filter but keeps the page size', async () => {
    const { router, user } = renderFilterBar(
      '/mobile-suits?work=w&q=zaku&unit_type=suit&limit=2&offset=2',
    );

    await user.click(screen.getByRole('button', { name: 'Clear filters' }));
    expect(router.state.location.search).toBe('?limit=2');
    expect(searchBox()).toHaveValue('');
    expect(
      screen.queryByRole('button', { name: 'Clear filters' }),
    ).not.toBeInTheDocument();
  });

  it('keeps a pending search when the user moves on to a filter', async () => {
    const { router, user } = renderFilterBar();

    await user.type(searchBox(), 'zaku');
    await user.selectOptions(
      screen.getByRole('combobox', { name: 'Unit type' }),
      'suit',
    );

    expect(router.state.location.search).toBe('?q=zaku&unit_type=suit');
  });

  it('drops a pending search when the URL changes while the box has focus', async () => {
    const { router, user } = renderFilterBar();

    await user.type(searchBox(), 'zaku');
    await act(() => router.navigate('/mobile-suits?unit_type=suit'));
    act(() => {
      vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS);
    });

    expect(router.state.location.search).toBe('?unit_type=suit');
    expect(searchBox()).toHaveValue('');
  });

  it('clears its timer on unmount', async () => {
    const { router, user } = renderFilterBar();

    await user.type(searchBox(), 'zaku');
    await act(() => router.navigate('/'));
    act(() => {
      vi.advanceTimersByTime(SEARCH_DEBOUNCE_MS);
    });

    expect(router.state.location.pathname).toBe('/');
    expect(vi.getTimerCount()).toBe(0);
  });
});
