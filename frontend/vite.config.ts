import { fileURLToPath, URL } from 'node:url';

import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

const safeSetInt = (val: unknown, fallback: number): number =>
  typeof val === 'string' ? parseInt(val, 10) : fallback;

export default defineConfig(() => {
  // TODO: read APP_DOMAIN and set `server.allowedHosts` (NODE-10) once Compose and the
  // reverse proxy exist.
  const { FRONTEND_PORT, LOG_LEVEL } = process.env;

  return {
    plugins: [react()],
    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
    },
    server: {
      host: true,
      port: safeSetInt(FRONTEND_PORT, 5173),
    },
    define: {
      'import.meta.env.LOG_LEVEL': JSON.stringify(LOG_LEVEL || 'INFO'),
    },
  };
});
