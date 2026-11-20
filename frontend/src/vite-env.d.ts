/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** @note Set from `LOG_LEVEL` through Vite `define` in `vite.config.ts` (REACT-31). */
  readonly LOG_LEVEL: import('loglevel').LogLevelDesc;
  /**
   * @description Whether the app answers its API calls from the Mirage fixtures.
   * @note Set from `MOCK_API` through Vite `define` in `vite.config.ts`, and always false
   * in a build.
   */
  readonly MOCK_API: boolean;
}
