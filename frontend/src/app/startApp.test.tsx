import { act, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { Server } from 'miragejs';
import type { Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { mockHealthCheckResponse } from '@/__mocks__/healthMocks';
import { makeMirageServer } from '@/__mocks__/mirageServer';

import { startApp } from './startApp';

describe('startApp', () => {
  let container: HTMLElement;
  let root: Root | undefined;
  let server: Server | undefined;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.append(container);
  });

  afterEach(() => {
    act(() => root?.unmount());
    server?.shutdown();
    container.remove();
    root = undefined;
    server = undefined;
  });

  it('renders the app without a mock server when none is asked for', async () => {
    root = await act(() => startApp(container));

    expect(
      await screen.findByRole('heading', { name: 'Welcome aboard' }),
    ).toBeInTheDocument();
  });

  it('starts the mock server before rendering, so its fixtures answer the API', async () => {
    root = await act(() =>
      startApp(container, {
        startMockApi: () => {
          expect(container).toBeEmptyDOMElement();
          server = makeMirageServer({ environment: 'test' });
          return Promise.resolve();
        },
      }),
    );

    await userEvent.click(screen.getByRole('link', { name: 'Health check' }));

    const healthCheckSection = await screen.findByRole('region', {
      name: 'Health Check',
    });
    expect(
      await within(healthCheckSection).findByText(mockHealthCheckResponse.data.status),
    ).toBeInTheDocument();
  });

  it('renders nothing when the mock server fails to start', async () => {
    await expect(
      startApp(container, {
        startMockApi: () => Promise.reject(new Error('no mock server')),
      }),
    ).rejects.toThrow('no mock server');

    expect(container).toBeEmptyDOMElement();
  });
});
