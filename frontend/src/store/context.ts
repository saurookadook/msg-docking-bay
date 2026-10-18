import { createContext } from 'react';

import type { Nullable } from '@/types';

import type { AppState } from './reducer';
import type { AppDispatch } from './types';

export type AppStoreContextValue = {
  appState: AppState;
  appDispatch: AppDispatch;
};

export const AppStoreContext = createContext<Nullable<AppStoreContextValue>>(null);
