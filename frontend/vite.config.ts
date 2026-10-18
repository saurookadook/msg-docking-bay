import { fileURLToPath, URL } from 'node:url';

import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

const safeSetInt = (val: unknown, fallback: number): number =>
  typeof val === 'string' ? parseInt(val, 10) : fallback;

/**
 * @description Read a variable the dev server cannot run without (NODE-10).
 * @throws {Error} When the variable is unset or empty.
 */
function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(
      `[requireEnv] : '${name}' must be set to serve the app (.env.example)`,
    );
  }
  return value;
}

export default defineConfig(({ command, mode }) => {
  const { FRONTEND_PORT, LOG_LEVEL } = process.env;
  // Only the dev server sits behind the proxy; Vitest (mode `test`) and Storybook also
  // load this file without it.
  const isProxiedDevServer =
    command === 'serve' && mode !== 'test' && process.env.STORYBOOK !== 'true';

  return {
    plugins: [react()],
    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
    },
    server: {
      host: true,
      port: safeSetInt(FRONTEND_PORT, 5173),
      strictPort: true,
      ...(isProxiedDevServer && {
        // The browser reaches Vite only through the proxy at https://APP_DOMAIN, so the
        // HMR socket connects to the proxy's port, not Vite's (ENV-37, ENV-40).
        allowedHosts: [requireEnv('APP_DOMAIN')],
        hmr: { clientPort: Number(requireEnv('PROXY_HTTPS_PORT')) },
      }),
    },
    define: {
      'import.meta.env.LOG_LEVEL': JSON.stringify(LOG_LEVEL || 'INFO'),
    },
  };
});
