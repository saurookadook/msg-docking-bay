import type { Decorator, Preview } from '@storybook/react-vite';
import { useState } from 'react';
import { createMemoryRouter, RouterProvider } from 'react-router';

import { makeMirageServer, type MirageRouteOverrides } from '@/__mocks__/mirageServer';
import { AppStoreProvider } from '@/store';

import '@/index.css';
import '@/app/App.css';

export type MirageParameters = {
  /** @description Route overrides for this story's Mirage server. */
  mirage?: MirageRouteOverrides;
  /** @description The path the story's memory router starts at. */
  route?: string;
};

function StoryRouter({
  initialEntry,
  Story,
}: {
  initialEntry: string;
  Story: React.ComponentType;
}) {
  const [router] = useState(() =>
    createMemoryRouter([{ path: '*', element: <Story /> }], {
      initialEntries: [initialEntry],
    }),
  );
  return <RouterProvider router={router} />;
}

const withAppProviders: Decorator = (Story, { parameters }) => (
  <AppStoreProvider>
    <StoryRouter
      initialEntry={(parameters as MirageParameters).route ?? '/'}
      Story={Story}
    />
  </AppStoreProvider>
);

const preview: Preview = {
  decorators: [withAppProviders],
  beforeEach({ parameters }) {
    const server = makeMirageServer({
      overrides: (parameters as MirageParameters).mirage,
    });
    return () => server.shutdown();
  },
};

export default preview;
