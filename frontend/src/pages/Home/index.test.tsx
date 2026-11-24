import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Server } from 'miragejs';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { renderWithProviders } from '@/utils/testing';

describe('Home', () => {
  let server: Server;

  beforeEach(() => {
    server = makeMirageServer({ environment: 'test' });
  });

  afterEach(() => {
    server.shutdown();
  });

  it('renders the welcome section at the root path', async () => {
    renderWithProviders({ initialEntries: ['/'] });

    const homeSection = await screen.findByRole('region', { name: 'Welcome aboard' });
    expect(
      within(homeSection).getByRole('heading', { level: 2, name: 'Welcome aboard' }),
    ).toBeVisible();
  });

  it('lists every bay, each opening its roster', async () => {
    const user = userEvent.setup();
    renderWithProviders({ initialEntries: ['/'] });

    const directory = await screen.findByRole('navigation', { name: 'Bay directory' });
    expect(
      within(directory)
        .getAllByRole('link')
        .map(({ textContent }) => textContent),
    ).toEqual(['Mobile Suits', 'Personnel', 'Organizations', 'Works', 'Designers']);
    await user.click(within(directory).getByRole('link', { name: 'Works' }));

    expect(
      await screen.findByRole('heading', { level: 2, name: /Works/ }),
    ).toBeVisible();
  });

  it('navigates to the health check page from its link', async () => {
    const user = userEvent.setup();
    renderWithProviders({ initialEntries: ['/'] });

    const homeSection = await screen.findByRole('region', { name: 'Welcome aboard' });
    await user.click(
      within(homeSection).getByRole('link', { name: 'health check page' }),
    );

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Health Check' }),
    ).toBeVisible();
  });
});
