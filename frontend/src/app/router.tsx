import type { RouteObject } from 'react-router';

import { Root } from '@/layouts';
import { HealthCheck, Home } from '@/pages';

/** @description Every route in the app. Tests build a memory router from it (REACT-24). */
export const routerConfig: RouteObject[] = [
  {
    path: '/',
    element: <Root />,
    children: [
      { index: true, element: <Home /> },
      { path: 'health-check', element: <HealthCheck /> },
    ],
  },
];
