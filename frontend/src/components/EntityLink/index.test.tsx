import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router';
import { describe, expect, it } from 'vitest';

import { EntityLink } from '.';

function renderInRouter(element: React.ReactElement) {
  const router = createMemoryRouter([{ path: '*', element }]);
  return render(<RouterProvider router={router} />);
}

describe('EntityLink', () => {
  it("links to the entity's page by its slug", () => {
    renderInRouter(
      <EntityLink kind="mobileSuit" slug="rx-78-2-gundam">
        RX-78-2 Gundam
      </EntityLink>,
    );

    expect(screen.getByRole('link', { name: 'RX-78-2 Gundam' })).toHaveAttribute(
      'href',
      '/mobile-suits/rx-78-2-gundam',
    );
  });

  it("keeps the kind's icon out of the link's name", () => {
    renderInRouter(
      <EntityLink kind="character" slug="amuro-ray">
        Amuro Ray
      </EntityLink>,
    );

    expect(screen.getByRole('link')).toHaveAccessibleName('Amuro Ray');
  });
});
