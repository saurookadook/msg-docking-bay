import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider, useParams } from 'react-router';
import { describe, expect, it } from 'vitest';

import type { DetailState } from '@/store';
import type { AppParams } from '@/types';

import { CatalogDetail } from '.';

type Detail = { name: string; slug: string };

function detailState(overrides: Partial<DetailState<Detail>>): DetailState<Detail> {
  return {
    detail: null,
    errorMessage: null,
    isNotFound: false,
    requestInProgress: false,
    ...overrides,
  };
}

/** @description The frame as a page mounts it: its slug read from the route. */
function Frame({ state }: { state: DetailState<Detail> | undefined }) {
  const { workSlug = '' } = useParams<AppParams>();
  return (
    <CatalogDetail
      detailState={state}
      id="work-details"
      kind="work"
      loadingHeading="Operation log"
      loadingLabel="Opening the log"
      notFound={<p>Cage empty</p>}
      slug={workSlug}
    >
      {(detail) => <h2>{detail.name}</h2>}
    </CatalogDetail>
  );
}

/**
 * @description Renders the frame at `/works/<slug><search>`.
 * @note A stub route, not the app's `routerConfig`: this tests the frame alone, from the
 * detail state it is given. Each page's test drives the real route and store.
 */
function renderFrame({
  search = '',
  slug,
  state,
}: {
  search?: string;
  slug: string;
  state: DetailState<Detail> | undefined;
}) {
  const router = createMemoryRouter(
    [{ path: '/works/:workSlug', element: <Frame state={state} /> }],
    { initialEntries: [`/works/${slug}${search}`] },
  );
  render(<RouterProvider router={router} />);
  return router;
}

describe('CatalogDetail', () => {
  describe('when the detail is loading', () => {
    it('shows the busy lamp in a section named by its hidden heading', () => {
      renderFrame({ slug: 'msg', state: undefined });

      expect(screen.getByRole('region', { name: 'Operation log' })).toHaveAttribute(
        'id',
        'work-details',
      );
      expect(screen.getByRole('status')).toHaveTextContent('Opening the log');
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('when the request fails', () => {
    it("shows the API's message instead of the lamp after an error", () => {
      renderFrame({
        slug: 'msg',
        state: detailState({ errorMessage: 'Service unavailable' }),
      });

      expect(screen.getByRole('alert')).toHaveTextContent('Service unavailable');
      expect(screen.getByRole('status')).toBeEmptyDOMElement();
    });
  });

  describe('when the entity is not found', () => {
    it('shows the not-found page on a 404', () => {
      renderFrame({
        slug: 'msg',
        state: detailState({ errorMessage: 'Work not found', isNotFound: true }),
      });

      expect(screen.getByText('Cage empty')).toBeVisible();
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  describe('when the entity is loaded', () => {
    it('renders the loaded entity', () => {
      renderFrame({
        slug: 'mobile-suit-gundam',
        state: detailState({
          detail: { name: 'Mobile Suit Gundam', slug: 'mobile-suit-gundam' },
        }),
      });

      expect(screen.getByRole('heading', { name: 'Mobile Suit Gundam' })).toBeVisible();
    });
  });

  describe('when the slug is old', () => {
    it('swaps an old slug for the current one, keeping the search and replacing the entry', async () => {
      const router = renderFrame({
        search: '?offset=50',
        slug: 'msg',
        state: detailState({
          detail: { name: 'Mobile Suit Gundam', slug: 'mobile-suit-gundam' },
        }),
      });

      expect(
        await screen.findByRole('heading', { name: 'Mobile Suit Gundam' }),
      ).toBeVisible();
      expect(router.state.location).toMatchObject({
        pathname: '/works/mobile-suit-gundam',
        search: '?offset=50',
      });
      expect(router.state.historyAction).toBe('REPLACE');
    });
  });
});
