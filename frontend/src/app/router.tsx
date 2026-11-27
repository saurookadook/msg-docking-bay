import type { RouteObject } from 'react-router';

import { Root } from '@/layouts';
import {
  CharacterList,
  DesignerList,
  HealthCheck,
  Home,
  MobileSuitDetails,
  MobileSuitList,
  NotFound,
  OrganizationList,
  WorkList,
} from '@/pages';

/** @description Every route in the app. Tests build a memory router from it (REACT-24). */
export const routerConfig: RouteObject[] = [
  {
    path: '/',
    element: <Root />,
    children: [
      { index: true, element: <Home /> },
      { path: 'health-check', element: <HealthCheck /> },
      { path: 'characters', element: <CharacterList /> },
      { path: 'mechanical-designers', element: <DesignerList /> },
      { path: 'mobile-suits', element: <MobileSuitList /> },
      { path: 'mobile-suits/:mobileSuitSlug', element: <MobileSuitDetails /> },
      { path: 'organizations', element: <OrganizationList /> },
      { path: 'works', element: <WorkList /> },
      { path: '*', element: <NotFound /> },
    ],
  },
];
