import { render } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router';

import { routerConfig } from '@/app/router';
import { AppStoreProvider, type AppState } from '@/store';

/**
 * @description Renders the app at `initialEntries` with the real store and router
 * (TEST-17).
 * @returns the render result, and the router, for tests that read or move the URL
 */
export function renderWithProviders({
  initialEntries = ['/'],
  initialState,
}: {
  initialEntries?: string[];
  initialState?: AppState;
} = {}) {
  const router = createMemoryRouter(routerConfig, { initialEntries });
  return {
    ...render(
      <AppStoreProvider initialState={initialState}>
        <RouterProvider router={router} />
      </AppStoreProvider>,
    ),
    router,
  };
}
