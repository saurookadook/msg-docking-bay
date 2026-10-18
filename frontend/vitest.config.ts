import { defineConfig, mergeConfig } from 'vitest/config';

import viteConfig from './vite.config.ts';

export default defineConfig((configEnv) =>
  mergeConfig(
    viteConfig(configEnv),
    defineConfig({
      test: {
        environment: 'jsdom',
        globals: false,
        setupFiles: ['./src/utils/testing/setupTests.ts'],
        include: ['src/**/*.test.{ts,tsx}'],
        coverage: {
          provider: 'v8',
          include: ['src/**/*.{ts,tsx}'],
          exclude: [
            'src/**/*.stories.tsx',
            'src/**/*.test.{ts,tsx}',
            'src/__mocks__/**',
            'src/utils/testing/**',
            'src/main.tsx',
          ],
        },
      },
    }),
  ),
);
