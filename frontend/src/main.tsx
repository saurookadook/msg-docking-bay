import { startApp } from '@/app/startApp';
import { sharedLog } from '@/utils';

import './index.css';

sharedLog.setLevel(import.meta.env.LOG_LEVEL, false);

const logger = sharedLog.getLogger('main');

const rootElement = document.getElementById('root');
if (rootElement == null) {
  throw new Error("[main] : Missing the '#root' element in index.html");
}

// `MOCK_API` is the constant `false` in a build, so Vite drops this import (TEST-18).
async function startMockApi(): Promise<void> {
  const { makeMirageServer } = await import('@/__mocks__/mirageServer');
  makeMirageServer({ environment: 'development' });
  logger.info(
    '[startMockApi] : Answering API calls from the Mirage fixtures (MOCK_API)',
  );
}

startApp(rootElement, {
  startMockApi: import.meta.env.MOCK_API ? startMockApi : undefined,
}).catch((error: unknown) => {
  logger.error('[main] : The app failed to start', error);
});
