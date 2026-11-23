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

function renderPagination({ meta, url }: { meta: PageMeta; url: string }) {
  const router = createMemoryRouter(
    [
      {
        path: '*',
        element: (
          <>
            <Pagination meta={meta} />
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

  it('marks the missing previous page as unavailable, not as a link', () => {
    renderPagination({
      meta: { limit: 50, offset: 0, total: 120 },
      url: '/mobile-suits',
    });

    expect(screen.queryByRole('link', { name: 'Previous' })).not.toBeInTheDocument();
    expect(screen.getByText('Previous')).toHaveAttribute('aria-disabled', 'true');
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

  it('renders nothing when every row fits on one page', () => {
    renderPagination({
      meta: { limit: 50, offset: 0, total: 3 },
      url: '/mobile-suits',
    });

    expect(screen.queryByRole('navigation')).not.toBeInTheDocument();
  });
});
