import { render } from '@testing-library/react';

import { AppStoreProvider, type AppState } from '@/store';

import { WithMemoryRouter } from './WithMemoryRouter';

/**
 * @description Renders the app at `initialEntries` with the real store and router
 * (TEST-17).
 */
export function renderWithProviders({
  initialEntries, // force formatting
  initialState,
}: {
  initialEntries?: string[];
  initialState?: AppState;
} = {}) {
  return render(
    <AppStoreProvider initialState={initialState}>
      <WithMemoryRouter initialEntries={initialEntries} />
    </AppStoreProvider>,
  );
}
