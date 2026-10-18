import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

import { sharedLog } from '@/utils';

// NOTE: the test run is a process entry point, so it sets the log level once (LOG-2).
// Expected request failures log at `error`; set LOG_LEVEL=DEBUG to see them.
sharedLog.setLevel(process.env.LOG_LEVEL === undefined ? 'SILENT' : 'DEBUG', false);

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
