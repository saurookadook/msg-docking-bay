import { useState } from 'react';
import { createMemoryRouter, RouterProvider } from 'react-router';

import { routerConfig } from '@/app/router';

export type WithMemoryRouterProps = {
  initialEntries?: string[];
};

/** @description Renders the app's real routes in a memory router (TEST-17). */
export function WithMemoryRouter({ initialEntries = ['/'] }: WithMemoryRouterProps) {
  const [router] = useState(() => createMemoryRouter(routerConfig, { initialEntries }));
  return <RouterProvider router={router} />;
}
