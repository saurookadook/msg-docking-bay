import { createRoot, type Root } from 'react-dom/client';

import App from './App';

/**
 * @description Renders the app into `container`, first awaiting `startMockApi` when it's
 * given, so no API call goes out before the mock server can answer it.
 * @note `main.tsx` passes `startMockApi` only when `MOCK_API` is on, and builds the
 * Mirage import inside it, so the bundler can drop the import from a build.
 * @returns the React root, for a caller that needs to unmount it
 * @throws when `startMockApi` rejects, in which case nothing renders
 */
export async function startApp(
  container: HTMLElement,
  { startMockApi }: { startMockApi?: () => Promise<void> } = {},
): Promise<Root> {
  await startMockApi?.();

  const root = createRoot(container);
  root.render(<App />);
  return root;
}
