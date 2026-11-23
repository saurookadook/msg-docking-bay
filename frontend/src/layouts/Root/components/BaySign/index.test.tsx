import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router';
import { describe, expect, it } from 'vitest';

import { BaySign } from '.';

function renderInRouter(element: React.ReactElement, url = '/') {
  const router = createMemoryRouter([{ path: '*', element }], {
    initialEntries: [url],
  });
  return render(<RouterProvider router={router} />);
}

describe('BaySign', () => {
  it("links a commissioned bay to its list and marks it while it's open", () => {
    renderInRouter(
      <BaySign isCommissioned kind="mobileSuit" label="Mobile Suits" />,
      '/mobile-suits',
    );

    const sign = screen.getByRole('link', { name: 'Mobile Suits' });
    expect(sign).toHaveAttribute('href', '/mobile-suits');
    expect(sign).toHaveAttribute('aria-current', 'page');
  });

  it('shows an uncommissioned bay as offline, not as a link', () => {
    renderInRouter(<BaySign isCommissioned={false} kind="work" label="Works" />);

    expect(screen.queryByRole('link')).not.toBeInTheDocument();
    expect(screen.getByText('Works')).toHaveTextContent('Works Offline');
  });
});
