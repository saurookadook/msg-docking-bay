import { useMemo, useReducer } from 'react';

import { AppStoreContext } from './context';
import { appReducer, initialAppState, type AppState } from './reducer';

export type AppStoreProviderProps = React.PropsWithChildren<{
  initialState?: AppState;
}>;

export function AppStoreProvider({
  children, // force formatting
  initialState = initialAppState,
}: AppStoreProviderProps) {
  const [appState, appDispatch] = useReducer(appReducer, initialState);
  const storeValue = useMemo(() => ({ appState, appDispatch }), [appState]);

  return <AppStoreContext value={storeValue}>{children}</AppStoreContext>;
}
