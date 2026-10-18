import { use } from 'react';

import { AppStoreContext, type AppStoreContextValue } from './context';

/** @description Reads and writes the app store (REACT-18). */
export function useAppStore(): AppStoreContextValue {
  const storeValue = use(AppStoreContext);
  if (storeValue == null) {
    throw new Error('[useAppStore] : must be called inside <AppStoreProvider>');
  }
  return storeValue;
}
