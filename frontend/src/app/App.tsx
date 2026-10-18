import { createBrowserRouter, RouterProvider } from 'react-router';

import { AppStoreProvider } from '@/store';

import { routerConfig } from './router';

import './App.css';

const router = createBrowserRouter(routerConfig);

export default function App() {
  return (
    <AppStoreProvider>
      <RouterProvider router={router} />
    </AppStoreProvider>
  );
}
