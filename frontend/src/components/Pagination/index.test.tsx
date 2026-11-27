import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createMemoryRouter, RouterProvider, useLocation } from 'react-router';
import { describe, expect, it } from 'vitest';

import type { PageMeta } from '@/api';

import { Pagination } from '.';

function LocationReadout() {
  const location = useLocation();
  return (
    <output aria-label="Location">{`${location.pathname}${location.search}`}</output>
  );
}

// NOTE: Pagination is not a route in routerConfig, so it can't be reached through
// WithMemoryRouter (TEST-17); a catch-all route renders it in a real router instead.
function renderPagination({
  meta,
  offsetParam,
  url,
}: {
  meta: PageMeta;
  offsetParam?: string;
  url: string;
}) {
  const router = createMemoryRouter(
    [
      {
        path: '*',
        element: (
          <>
            <Pagination meta={meta} offsetParam={offsetParam} />
            <LocationReadout />
          </>
        ),
      },
    ],
    { initialEntries: [url] },
  );
  return render(<RouterProvider router={router} />);
}

describe('Pagination', () => {
  it('shows the rows on this page and keeps other params on the next link', async () => {
    const user = userEvent.setup();
    renderPagination({
      meta: { limit: 50, offset: 0, total: 120 },
      url: '/mobile-suits?continuity=universal-century',
    });

    const pagination = screen.getByRole('navigation', { name: 'Pagination' });
    expect(within(pagination).getByText('1–50 of 120')).toBeVisible();
    await user.click(within(pagination).getByRole('link', { name: 'Next' }));

    expect(screen.getByRole('status', { name: 'Location' })).toHaveTextContent(
      '/mobile-suits?continuity=universal-century&offset=50',
    );
  });

  it('names the missing previous page as unavailable, not as a link', () => {
    renderPagination({
      meta: { limit: 50, offset: 0, total: 120 },
      url: '/mobile-suits',
    });

    expect(screen.queryByRole('link', { name: 'Previous' })).not.toBeInTheDocument();
    expect(screen.getByText('Previous')).toHaveTextContent('Previous (unavailable)');
  });

  it('drops the offset param when going back to the first page', async () => {
    const user = userEvent.setup();
    renderPagination({
      meta: { limit: 50, offset: 50, total: 120 },
      url: '/mobile-suits?offset=50',
    });

    await user.click(screen.getByRole('link', { name: 'Previous' }));

    expect(screen.getByRole('status', { name: 'Location' })).toHaveTextContent(
      /^\/mobile-suits$/,
    );
  });

  it('says no rows show on a page past the end', () => {
    renderPagination({
      meta: { limit: 50, offset: 400, total: 120 },
      url: '/mobile-suits?offset=400',
    });

    expect(screen.getByText('None of 120')).toBeVisible();
  });

  it('pages through its own offset param, leaving the page offset alone', async () => {
    const user = userEvent.setup();
    renderPagination({
      meta: { limit: 2, offset: 2, total: 5 },
      offsetParam: 'operator_offset',
      url: '/organizations/earth-federation?offset=4&operator_offset=2',
    });

    await user.click(screen.getByRole('link', { name: 'Next' }));
    expect(screen.getByRole('status', { name: 'Location' })).toHaveTextContent(
      '/organizations/earth-federation?offset=4&operator_offset=4',
    );

    // NOTE: the meta stays at offset 2, so Previous goes to the first page.
    await user.click(screen.getByRole('link', { name: 'Previous' }));
    expect(screen.getByRole('status', { name: 'Location' })).toHaveTextContent(
      /^\/organizations\/earth-federation\?offset=4$/,
    );
  });

  it('renders nothing when every row fits on one page', () => {
    renderPagination({
      meta: { limit: 50, offset: 0, total: 3 },
      url: '/mobile-suits',
    });

    expect(screen.queryByRole('navigation')).not.toBeInTheDocument();
  });
});
