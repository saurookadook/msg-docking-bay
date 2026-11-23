import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Server } from 'miragejs';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { renderWithProviders } from '@/utils/testing';

describe('NotFound', () => {
  let server: Server;

  beforeEach(() => {
    server = makeMirageServer({ environment: 'test' });
  });

  afterEach(() => {
    server.shutdown();
  });

  it('shows an empty cage for a path no route matches', async () => {
    renderWithProviders({ initialEntries: ['/no-such-bay'] });

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Cage empty' }),
    ).toBeVisible();
    expect(screen.getByText('NO UNIT ASSIGNED TO /no-such-bay')).toBeVisible();
  });

  it('leaves known routes to their own pages', async () => {
    renderWithProviders({ initialEntries: ['/health-check'] });

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Health Check' }),
    ).toBeVisible();
    expect(
      screen.queryByRole('heading', { name: 'Cage empty' }),
    ).not.toBeInTheDocument();
  });

  it('links back to the deck', async () => {
    const user = userEvent.setup();
    renderWithProviders({ initialEntries: ['/no-such-bay'] });

    await user.click(await screen.findByRole('link', { name: 'Return to the deck' }));

    expect(
      await screen.findByRole('heading', { level: 2, name: 'Welcome aboard' }),
    ).toBeVisible();
  });
});
