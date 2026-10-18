/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** @note Set from `LOG_LEVEL` through Vite `define` in `vite.config.ts` (REACT-31). */
  readonly LOG_LEVEL: import('loglevel').LogLevelDesc;
}
