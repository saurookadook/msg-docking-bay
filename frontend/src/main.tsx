import { createRoot } from 'react-dom/client';

import App from '@/app/App';
import { sharedLog } from '@/utils';

import './index.css';

sharedLog.setLevel(import.meta.env.LOG_LEVEL, false);

const logger = sharedLog.getLogger('main');

const rootElement = document.getElementById('root');
if (rootElement == null) {
  throw new Error("[main] : Missing the '#root' element in index.html");
}

/**
 * @description Renders the app, first starting the Mirage server when `MOCK_API` is on.
 * @note `MOCK_API` is the constant `false` in a build, so Vite drops the import.
 */
async function start(root: HTMLElement): Promise<void> {
  if (import.meta.env.MOCK_API) {
    const { makeMirageServer } = await import('@/__mocks__/mirageServer');
    makeMirageServer({ environment: 'development' });
    logger.info('[start] : Answering API calls from the Mirage fixtures (MOCK_API)');
  }

  createRoot(root).render(<App />);
}

start(rootElement).catch((error: unknown) => {
  logger.error('[start] : The app failed to start', error);
});
