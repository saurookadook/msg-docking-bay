import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Server } from 'miragejs';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { makeMirageServer } from '@/__mocks__/mirageServer';
import { SHIFT_LS_KEY } from '@/constants';
import { renderWithProviders } from '@/utils/testing';

describe('Root', () => {
  let server: Server;

  beforeEach(() => {
    server = makeMirageServer({ environment: 'test' });
  });

  afterEach(() => {
    server.shutdown();
  });

  it('shows the deck status bar with the bay name and the shift toggle', async () => {
    renderWithProviders({ initialEntries: ['/'] });

    const statusBar = await screen.findByRole('banner');
    expect(
      within(statusBar).getByRole('heading', { level: 1, name: 'MSG Docking Bay' }),
    ).toBeVisible();
    expect(within(statusBar).getByText('Deck online')).toBeVisible();
    expect(within(statusBar).getByRole('group', { name: 'Shift' })).toBeVisible();
  });

  it('shows every bay sign, with uncommissioned bays offline and not linked', async () => {
    renderWithProviders({ initialEntries: ['/'] });

    const bays = await screen.findByRole('navigation', { name: 'Bays' });
    for (const label of [
      'Mobile Suits',
      'Personnel',
      'Organizations',
      'Works',
      'Designers',
    ]) {
      const sign = within(bays).getByText(label);
      expect(sign).toHaveAttribute('aria-disabled', 'true');
      expect(sign).toHaveTextContent(`${label} Offline`);
    }
    expect(within(bays).queryByRole('link')).not.toBeInTheDocument();
  });

  it('starts the shift toggle on the stored shift', async () => {
    localStorage.setItem(SHIFT_LS_KEY, JSON.stringify('night'));
    renderWithProviders({ initialEntries: ['/'] });

    expect(await screen.findByRole('radio', { name: 'Night' })).toBeChecked();
    expect(document.documentElement).toHaveAttribute('data-shift', 'night');
  });

  it('credits the sources and disclaims the franchise in the footer', async () => {
    renderWithProviders({ initialEntries: ['/'] });

    const footer = await screen.findByRole('contentinfo');
    expect(within(footer).getByText(/unofficial fan project/)).toBeVisible();
    expect(within(footer).getByRole('link', { name: 'Gundam Wiki' })).toHaveAttribute(
      'href',
      'https://gundam.fandom.com/',
    );
  });

  it('reaches the health check from the footer and home from the bay name', async () => {
    const user = userEvent.setup();
    renderWithProviders({ initialEntries: ['/'] });

    await user.click(
      within(await screen.findByRole('contentinfo')).getByRole('link', {
        name: 'Deck systems',
      }),
    );
    expect(
      await screen.findByRole('heading', { level: 2, name: 'Health Check' }),
    ).toBeVisible();

    await user.click(screen.getByRole('link', { name: 'MSG Docking Bay' }));
    expect(
      await screen.findByRole('heading', { level: 2, name: 'Welcome aboard' }),
    ).toBeVisible();
  });
});
